import copy
import hashlib
import json
from pathlib import Path
import math
import os
import pickle
import sys
import warnings

from matplotlib import pyplot as plt
import numpy as np
from omegaconf import DictConfig, OmegaConf
import torch
from torchvision.utils import make_grid
import deepinv as dinv
from deepinv.optim.data_fidelity import L2
from deepinv.optim.optimizers import optim_builder
from deepinv.optim.dpir import get_DPIR_params
from deepinv.utils.parameters import get_GSPnP_params

from ddm4ip.data.base import Batch, Datasplit, init_dataset
from ddm4ip.degradations.degradation import init_noise
from ddm4ip.losses.deepinv_loss import DeepInvLoss
from ddm4ip.networks.blur_nets import BlurDegradationType
from ddm4ip.trainers.base import BaseTrainer, init_trts_dataloaders
from ddm4ip.trainers.plots import plot_spacevarying_kernels
from ddm4ip.utils import distributed
from ddm4ip.utils.deepinv_utils import DinvReconstructorWrapper, GSPnP, WienerSolver, DPSWrapper
from ddm4ip.utils.benchmark_metrics import BenchmarkMetricWriter, canonical_json_sha256
from ddm4ip.utils.diffpir import DiffPIR
from ddm4ip.utils.torch_utils import write_img_pt


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _load_pickle_with_project_path(path: Path):
    original_sys_path = list(sys.path)
    project_root = str(Path(__file__).resolve().parents[2])
    try:
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        with Path(path).open("rb") as handle:
            return pickle.load(handle)
    finally:
        sys.path[:] = original_sys_path


class DeepinvDenoiserTrainer(BaseTrainer):
    """
    Inverse problem solver wrapping [DeepInv](https://deepinv.github.io/) implementations.
    This class takes in a **paired dataset**, which is generated through our learned
    inverse operator. It then uses DeepInv to attempt to invert this operator through standard
    methods:
     - GSPnP (copied from the [deepinv tutorial](https://deepinv.github.io/deepinv/auto_examples/plug-and-play/demo_RED_GSPnP_SR.html))

    Be careful when instantiating the dataset:
     - it should use the "true" corruption process to generate samples.
     - the modeled corruption process should be used to initialize the DeepInv model
    """
    def __init__(self):
        super().__init__()
        self.plot_dloader = None
        self.physics = None
        self.quantitative = False

    def init_datasets(self, cfg: DictConfig):
        self.require_output_manifest = cfg.training.get("require_output_manifest", False)
        return {
            # This dataset should be paired!
            Datasplit.TEST: init_dataset(cfg, split=Datasplit.TEST, is_paired=True)
        }

    def init_dataloaders(self, cfg, dsets):
        # No infinite data-loader because we want to loop through the test
        # dataset once only.
        return init_trts_dataloaders(
            cfg, dsets, start_idx=self.start_global_step, is_infinite=False
        )

    def init_gspnp(self, prior_model, noise_level):
        # Parameters here are mostly copied from the deepinv tutorial on GSPnP.
        prior = GSPnP(denoiser=prior_model)
        lamb, sigma_denoiser, stepsize, max_iter = get_GSPnP_params("deblur", noise_level)
        params_algo = {
            "stepsize": stepsize,
            "g_param": sigma_denoiser,
            "lambda": lamb,
        }
        # we want to output the intermediate PGD update to finish with a denoising step.
        def custom_output(X):
            return X["est"][1]
        optim_params = {
            "iteration": "PGD",
            "g_first": True,
            "max_iter": max_iter,
            "params_algo": params_algo,
            "data_fidelity": L2(),
            "prior": prior,
            "get_output": custom_output,
            "backtracking": True,
            "early_stop": True,  # Stop algorithm when convergence criteria is reached
            "crit_conv": "cost",  # Convergence is reached when the difference of cost function between consecutive iterates is smaller than thres_conv
            "thres_conv": 1e-4,
        }
        return optim_builder(verbose=False, **optim_params)

    def init_dpir(self, prior_model, noise_level):
        prior = dinv.optim.prior.PnP(prior_model)
        sigma_denoiser, stepsize, max_iter = get_DPIR_params(noise_level)
        optim_params = {
            "params_algo": {
                "stepsize": stepsize,
                "g_param": sigma_denoiser,
            },
            "iteration": "HQS",
            "prior": prior,
            "data_fidelity": L2(),
            "max_iter": max_iter,
            "backtracking": False,
            "early_stop": False,
        }
        return optim_builder(verbose=False, **optim_params)

    def init_dps(self, model, max_iter, eta, device):
        dps_model = DPSWrapper(
            model=model,
            data_fidelity=L2(),
            max_iter=max_iter,
            eta=eta,
            device=device,
            save_iterates=True,
        )
        return DinvReconstructorWrapper(dps_model)

    def init_diffpir(self, model, noise_level, max_iter=100, zeta=0.3, lambda_=6.0):
        diffpir_model = DiffPIR(
            model=model,
            data_fidelity=L2(),
            max_iter=max_iter,
            zeta=zeta,
            lambda_=lambda_,
            sigma=noise_level
        )
        return DinvReconstructorWrapper(diffpir_model)

    def init_wiener(self, balance):
        wiener_deconv = WienerSolver(balance=balance)
        return DinvReconstructorWrapper(wiener_deconv)

    def init_deep_prior(self, network: str, device, **kwargs):
        if network.lower() == "drunet":
            model = dinv.models.DRUNet(pretrained="download").to(device=device)
            distributed.print0("Initialized DRUNet prior")
        elif network.lower() == "diffunet":
            large_model = kwargs.get("large_model", False)
            model = dinv.models.DiffUNet(large_model=large_model, use_fp16=False, pretrained="download").to(device=device)
            distributed.print0(f"Initialized DiffUNet-{'large' if large_model else 'small'} prior")
        else:
            raise ValueError(f"Network '{network}' is not a valid deep prior.")
        return model

    def init_models(self, cfg, dsets, device):
        models = {}
        test_dset = dsets[Datasplit.TEST]
        assert test_dset is not None
        # Initialize perturbation model
        if "kernel" in cfg.models and (pert_path := cfg.models.kernel.get("path")) is not None:
            if not pert_path.endswith(".pkl"):
                raise ValueError(
                    f"Cannot load degradation model from '{pert_path}'. "
                    "The file must be a pickle (network-snapshot) file."
                )
            pretr_data = _load_pickle_with_project_path(Path(pert_path))
            kernel_nn = pretr_data["kernel_nn"]
            models["kernel_nn"] = kernel_nn.to(device)
        else:
            print("No kernel-NN loaded. Will use the default degradation!")
            models["kernel_nn"] = copy.deepcopy(test_dset.corruption).to(device)
            if hasattr(models["kernel_nn"], "device"):
                models["kernel_nn"].device = device

        # Initialize the DeepInv solver model
        noise_level = self.get_noise_level(test_dset, models["kernel_nn"])
        invp_cfg = cfg["models"]["deepinv_solver"]
        solver_method = invp_cfg["method"]
        if solver_method.lower() == "gspnp":
            prior = self.init_deep_prior("drunet", device)
            models["deepinv_model"] = self.init_gspnp(prior, noise_level)
        elif solver_method.lower() == "dpir":
            prior = self.init_deep_prior(invp_cfg["prior"], device, **invp_cfg)
            models["deepinv_model"] = self.init_dpir(prior, noise_level)
        elif solver_method.lower() == "dps":
            prior = self.init_deep_prior(invp_cfg["prior"], device, **invp_cfg)
            models["deepinv_model"] = self.init_dps(
                prior, max_iter=invp_cfg["max_iter"], eta=invp_cfg.get("eta", 1.0), device=device
            )
        elif solver_method.lower() == "diffpir":
            prior = self.init_deep_prior(invp_cfg["prior"], device, **invp_cfg)
            models["deepinv_model"] = self.init_diffpir(
                prior, noise_level=invp_cfg.get("sigma", noise_level), max_iter=invp_cfg.get("max_iter", 100),
                zeta=invp_cfg.get("zeta", 0.3), lambda_=invp_cfg.get("lambda_", 8.0)
            )
        elif solver_method.lower() == "wiener":
            models["deepinv_model"] = self.init_wiener(
                balance=invp_cfg.get("balance", noise_level)
            )
        else:
            raise ValueError(f"deepinv_solver method '{solver_method}' is invalid.")

        return models

    def get_physics(self, cfg) -> dinv.physics.Physics:
        # The physics is the one modeled and learned using DiffInstruct
        from ddm4ip.degradations.blur import Blur
        from ddm4ip.degradations.varpsf import PerPixelBlur
        from ddm4ip.degradations.downsampling import Downsampling
        kernel_nn = self.models["kernel_nn"]
        if self.physics is None:
            noise_sigma = self.get_noise_level(self.dsets[Datasplit.TEST], kernel_nn)
            noise_model = init_noise({"kind": "gaussian", "std": noise_sigma})

            if (deg_type := getattr(kernel_nn, "degradation_type", None)) is not None:
                if deg_type == BlurDegradationType.BLUR:
                    self.physics = Blur(
                        filter=None,
                        padding="replicate",  # Shouldn't be 'valid', or the complex and brittle patching code fails
                        noise_model=noise_model,
                        device=self.device  # type: ignore
                    )
                elif deg_type == BlurDegradationType.PER_PIXEL_BLUR:
                    self.physics = PerPixelBlur(
                        filters=None,
                        padding=kernel_nn.padding,
                        noise_model=noise_model,
                        device=self.device  # type: ignore
                    )
                elif deg_type == BlurDegradationType.DOWNSAMPLING:
                    dset = self.dsets[Datasplit.TEST]
                    assert dset is not None
                    self.physics = Downsampling(
                        filter=None,
                        padding="reflect",#kernel_nn.padding,
                        img_size=dset.clean_img_size,
                        device=self.device  # type: ignore
                    )
                else:
                    raise NotImplementedError(deg_type)
            elif isinstance(kernel_nn, dinv.physics.Physics):
                # path taken when doing baselines (true degradation kernels)
                # Adapter speeds up baseline when using per-pixel blurs
                # self.physics = SpaceToCenterAdapter(kernel_nn, img_h=128, img_w=128)
                # Keep the frozen baseline kernel separate from the mutable solver
                # physics. run_on_data crops and updates the latter for each batch;
                # aliasing them would shrink the source filter on every sample.
                self.physics = copy.deepcopy(kernel_nn)
            else:
                raise ValueError("Failed to initialize physics for the provided step-2 NN.")
            distributed.print0(f"Initialized physics: {self.physics}")

        return self.physics

    def get_noise_level(self, test_dset, kernel_model) -> float:
        if hasattr(kernel_model, "sigma"):
            print(f"Overriding provided sigma with sigma from model ({kernel_model.sigma.item()})")
            noise_level = kernel_model.sigma
        else:
            # The noise-level is assumed to be known, hence we just load the true
            # value from the dataset
            noise_level = test_dset.noise_level
        return noise_level.item() if isinstance(noise_level, torch.Tensor) else noise_level

    def init_loss(self, cfg, models) -> DeepInvLoss:
        loss = DeepInvLoss(
            cfg,
            self.get_physics(cfg),
            deepinv_model=models["deepinv_model"],
            kernel_nn=models["kernel_nn"]
        )

        evaluation = cfg.get("evaluation", {})
        self.quantitative = bool(evaluation.get("quantitative", False))
        if self.quantitative:
            variant = evaluation.get("variant")
            step2_seed = evaluation.get("step2_seed", None)
            kernel_gt_path = evaluation.get("kernel_gt_path")
            expected_count = evaluation.get("expected_records")
            pairs_manifest_sha256 = evaluation.get("pairs_manifest_sha256")
            benchmark_summary_sha256 = evaluation.get("benchmark_summary_sha256")
            predecessor_network_snapshot_sha256 = evaluation.get(
                "predecessor_network_snapshot_sha256", None
            )
            if (
                variant not in {"oracle", "learned"}
                or kernel_gt_path is None
                or expected_count is None
                or pairs_manifest_sha256 is None
                or benchmark_summary_sha256 is None
            ):
                raise ValueError(
                    "quantitative evaluation requires variant, kernel, record count, and benchmark hashes"
                )
            pairs_path = Path(cfg.dataset.test.path)
            summary_path = Path(cfg.paths.data) / "summary.json"
            if not pairs_path.is_file() or not summary_path.is_file():
                raise ValueError("quantitative benchmark manifests are missing")
            if _file_sha256(pairs_path) != str(pairs_manifest_sha256).lower():
                raise ValueError("configured pairs_manifest_sha256 does not match dataset.test.path")
            if _file_sha256(summary_path) != str(benchmark_summary_sha256).lower():
                raise ValueError("configured benchmark_summary_sha256 does not match benchmark summary")
            solver_payload = {
                "deepinv_solver": OmegaConf.to_container(cfg.models.deepinv_solver, resolve=True),
                "loss": OmegaConf.to_container(cfg.loss, resolve=True),
            }
            solver_hash = canonical_json_sha256(solver_payload)
            self.metric_writer = BenchmarkMetricWriter(
                Path(self.eval_dir),
                experiment_id=str(cfg.exp_name),
                variant=variant,
                step2_seed=step2_seed,
                solver_config_sha256=solver_hash,
                kernel_gt_path=Path(kernel_gt_path),
                expected_count=int(expected_count),
                pairs_manifest_sha256=str(pairs_manifest_sha256),
                benchmark_summary_sha256=str(benchmark_summary_sha256),
                predecessor_network_snapshot_sha256=predecessor_network_snapshot_sha256,
            )
            claimed_kernel_hash = evaluation.get("kernel_gt_sha256", None)
            if claimed_kernel_hash is not None and self.metric_writer.kernel_gt_sha256.lower() != str(claimed_kernel_hash).lower():
                raise ValueError("configured kernel_gt_sha256 does not match kernel_gt_path")
            self.expected_pairs_manifest_sha256 = str(pairs_manifest_sha256)
            self.benchmark_summary_sha256 = str(benchmark_summary_sha256)
        return loss

    @staticmethod
    def _metadata_at(meta, key, index):
        value = meta[key]
        if isinstance(value, torch.Tensor):
            return value[index]
        if isinstance(value, (list, tuple)):
            return value[index]
        return value

    def _validate_quantitative_batch(self, val_batch: Batch):
        metrics, pred_img, filters = self.loss_optim.val_loss_with_output(self, val_batch)
        if val_batch.clean is None or val_batch.corrupt is None:
            raise ValueError("quantitative evaluation requires clean and noisy paired data")
        if "source_id" not in val_batch.meta:
            raise ValueError("quantitative evaluation requires source_id metadata")
        output_dir = Path(self.eval_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        geometry = getattr(self.loss_optim, "output_geometry", None)
        if not geometry or not geometry.get("filter_groups"):
            raise ValueError("quantitative evaluation requires solver geometry")
        batch_size = pred_img.shape[0]
        if batch_size != 1:
            raise ValueError("quantitative recording currently requires batch_size=1")

        prepared = []
        manifest_path = output_dir / "manifest.jsonl"
        existing_sources = set()
        if manifest_path.exists():
            for line in manifest_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    existing_sources.add(json.loads(line)["source_id"])
        for index in range(batch_size):
            source_id = self._metadata_at(val_batch.meta, "source_id", index)
            if not isinstance(source_id, str) or not source_id or Path(source_id).name != source_id:
                raise ValueError("source_id must be a safe filename stem")
            if source_id in existing_sources:
                raise FileExistsError("source image is already recorded")
            prediction_name = f"prediction-{source_id}.png"
            kernel_name = f"kernel-{source_id}.pt"
            prediction_path = output_dir / prediction_name
            kernel_path = output_dir / kernel_name
            if prediction_path.exists() or kernel_path.exists():
                raise FileExistsError("quantitative prediction artifact already exists")
            batch_meta = {
                key: self._metadata_at(val_batch.meta, key, index)
                for key in val_batch.meta
            }
            input_metrics = self.loss_optim.compute_img_metrics(
                val_batch.corrupt[index], val_batch.clean[index]
            )
            prediction_tensor = pred_img[index].detach().cpu()
            # Quantitative recording enforces batch_size=1; all leading filters
            # belong to this image's shared/per-tile geometry.
            kernel_tensor = filters.detach().cpu()
            if not write_img_pt(prediction_tensor, prediction_path):
                raise IOError(f"failed to write {prediction_path}")
            with kernel_path.open("xb") as handle:
                torch.save(kernel_tensor, handle)
            prediction_sha256 = _file_sha256(prediction_path)
            kernel_sha256 = _file_sha256(kernel_path)
            from ddm4ip.utils.torch_utils import read_img_pt
            restored_metrics = self.loss_optim.compute_img_metrics(
                read_img_pt(prediction_path), val_batch.clean[index]
            )
            serialized = self.metric_writer.prepare_record(
                batch_meta,
                prediction_tensor,
                kernel_tensor,
                prediction_name,
                kernel_name,
                geometry,
                input_metrics,
                restored_metrics,
                prediction_sha256=prediction_sha256,
                kernel_sha256=kernel_sha256,
            )
            metric_row = json.loads(serialized)
            manifest_row = {"schema_version": 2, **metric_row}
            json.dumps(manifest_row, ensure_ascii=False, allow_nan=False)
            prepared.append((serialized, manifest_row, prediction_path, kernel_path, index))

        manifest_lines = []
        for serialized, manifest_row, prediction_path, kernel_path, index in prepared:
            self.metric_writer.append(serialized)
            manifest_lines.append(json.dumps(manifest_row, ensure_ascii=False, allow_nan=False, sort_keys=True))
        if manifest_lines:
            with manifest_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write("\n".join(manifest_lines) + "\n")
        self.metric_writer.finalize_if_complete()
        return metrics

    def validate_batch(self, val_batch: Batch):
        if getattr(self, "quantitative", False):
            return self._validate_quantitative_batch(val_batch)
        metrics, pred_img, filters = self.loss_optim.val_loss_with_output(self, val_batch)
        if self.save_eval_to_file:
            assert self.eval_dir is not None and val_batch.corrupt is not None
            if self.save_pred_only or val_batch.clean is None:
                img_batch = pred_img.cpu()
            elif val_batch.corrupt.shape == val_batch.clean.shape:
                img_batch = torch.cat([val_batch.corrupt.cpu(), pred_img.cpu(), val_batch.clean.cpu()], dim=-1)
            else:
                img_batch = torch.cat([pred_img.cpu(), val_batch.clean.cpu()], dim=-1)
            assert img_batch.dim() == 4
            output_dir = Path(self.eval_dir)
            kernel_name = f"kernel_{self.global_step:05d}.pt"
            image_names = [f"img_{self.global_step + i:05d}.png" for i in range(len(img_batch))]
            paths = [output_dir / name for name in [kernel_name, *image_names]]
            # Check all destinations before touching any existing artifact.
            for path in paths:
                if path.exists():
                    raise FileExistsError(path)
            required = ("source_root", "source_path", "sample_index", "input_size",
                        "mode", "tile_index", "tile_coordinates")
            has_provenance = all(key in val_batch.meta for key in required)
            if getattr(self, "require_output_manifest", False) and not has_provenance:
                raise ValueError("Required output provenance is missing")
            records = []
            if has_provenance:
                if len(img_batch) != 1:
                    raise ValueError("Full-image provenance requires batch_size=1")
                geometry = getattr(self.loss_optim, "output_geometry", None)
                if not geometry or not geometry.get("filter_groups"):
                    raise ValueError("Solver kernel provenance is missing")
                record = {}
                for key in required:
                    value = val_batch.meta[key][0]
                    record[key] = value.tolist() if isinstance(value, torch.Tensor) else value
                record.update({
                    "schema_version": 1, "output_index": self.global_step,
                    "output_path": image_names[0], "output_size": list(pred_img.shape[-2:]),
                    "kernel_path": kernel_name, "kernel_shape": list(filters.shape),
                    "solver_geometry": geometry,
                    "metrics": {key: float(value) for key, value in metrics.items()},
                })
                manifest = output_dir / "manifest.jsonl"
                if manifest.exists():
                    for line in manifest.read_text(encoding="utf-8").splitlines():
                        previous = json.loads(line)
                        if (previous["output_path"] == record["output_path"]
                            or (previous["source_root"], previous["source_path"], previous["tile_index"])
                            == (record["source_root"], record["source_path"], record["tile_index"])):
                            raise FileExistsError("Prediction already recorded in manifest")
                # Serialize before writing artifacts to detect invalid metadata early.
                records.append(json.dumps(record, ensure_ascii=False, allow_nan=False))
            # A kernel tensor can contain shared or per-tile filters; the manifest
            # explicitly maps tile ranges to slices along its leading dimension.
            with (output_dir / kernel_name).open("xb") as fh:
                torch.save(filters, fh)
            for i, name in enumerate(image_names):
                if not write_img_pt(img_batch[i], str(output_dir / name)):
                    raise IOError(f'failed to write {output_dir / name}')
            if records:
                with (output_dir / "manifest.jsonl").open("a", encoding="utf-8") as fh:
                    for record in records:
                        fh.write(record + "\n")
        return metrics

    def make_plots(self, cfg, dsets, dloaders, models, tb_writer, global_step):
        if self.plot_dloader is None:
            if (dl := dloaders.get(Datasplit.TEST)) is None:
                warnings.warn("Using training batch for plotting.")
                dl = dloaders[Datasplit.TRAIN]
                assert dl is not None
            self.plot_dloader = iter(dl)

        try:
            plot_batch = next(self.plot_dloader)
        except StopIteration:
            return

        models["deepinv_model"].eval()
        testset = dsets[Datasplit.TEST]
        assert testset is not None

        p1 = self.plot_generated(plot_batch, models["deepinv_model"])
        if distributed.get_rank() == 0 and p1 is not None:
            self.log_image(p1, 'denoiser/generated', tb_writer)

        p2 = None
        try:
            p2, p2_ker = plot_spacevarying_kernels(
                testset.corruption,
                self.loss_optim.patch_size or testset.corrupt_img_size[-1],
                self.models["kernel_nn"],
                self.batch_size,
                self.device
            )
        except TypeError:
            pass
        if distributed.get_rank() == 0 and p2 is not None:
            self.log_image(p2, 'denoiser/kernels', tb_writer)

    @torch.no_grad()
    def plot_generated(self, batch: Batch, deepinv_model, num_imgs: int = 16):
        dev_batch = batch[:num_imgs].to(self.device)
        if dev_batch.clean is None:
            return None
        assert dev_batch.corrupt is not None
        target = dev_batch.clean
        source = dev_batch.corrupt

        preds, _ = self.loss_optim.run_model(dev_batch)

        batch_size = target.shape[0]
        n_img_row = int(math.sqrt(batch_size))

        target = make_grid(
            target.clamp(0, 1),
            nrow=n_img_row, padding=0,
        ).permute(1, 2, 0).numpy(force=True)
        source = make_grid(
            source.clamp(0, 1),
            nrow=n_img_row, padding=0,
        ).permute(1, 2, 0).numpy(force=True)
        preds = make_grid(
            preds.clamp_(0, 1),
            nrow=n_img_row, padding=0,
        ).permute(1, 2, 0).numpy(force=True)

        fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(6, 6))

        ax[0, 0].imshow(source, aspect='equal', interpolation='none')
        ax[0, 0].set_title(r"noisy")
        ax[0, 0].set_axis_off()

        ax[0, 1].imshow(target, aspect='equal', interpolation='none')
        ax[0, 1].set_title(r"clean")
        ax[0, 1].set_axis_off()

        ax[1, 0].imshow(preds, aspect='equal', interpolation='none')
        ax[1, 0].set_title(r"predicted")
        ax[1, 0].set_axis_off()

        diff = (target - preds).mean(2)  # average over channels
        title = r"errors"
        if np.abs(diff).max() < 0.1:
            diff *= 10
            title = rf"{title} (x10)"
        ax[1, 1].imshow(diff, aspect='equal', interpolation='none', cmap='RdBu', vmin=-1.0, vmax=1.0)
        ax[1, 1].set_title(title)
        ax[1, 1].set_axis_off()

        fig.tight_layout()
        return fig
