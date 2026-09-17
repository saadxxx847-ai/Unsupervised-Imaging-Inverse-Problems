import csv
import os
from pathlib import Path
import tempfile
import unittest

from scripts.build_bdd100k_views import build_view


class BDD100KViewBuilderTests(unittest.TestCase):
    def _write_image(self, directory: Path, name: str) -> Path:
        path = directory / name
        path.write_bytes(name.encode("ascii"))
        return path

    def _write_metrics(self, path: Path, blur_names: list[str]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["group", "filename", "laplacian_variance"])
            writer.writeheader()
            for index, name in enumerate(blur_names):
                writer.writerow({"group": "blurry", "filename": name, "laplacian_variance": index})

    def test_build_view_keeps_only_middle_blur_ranks_and_makes_hardlinks(self) -> None:
        """Would fail if Q1/Q4 are selected or outputs are copies rather than hardlinks."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            sharp_dir = root / "Kept_High_Score(Sharp)"
            blurry_dir = root / "Kept_Low_Score(Blurry)"
            sharp_dir.mkdir(parents=True)
            blurry_dir.mkdir(parents=True)
            sharp_names = [f"s{index:02d}.jpg" for index in range(20)]
            blur_names = [f"b{index:02d}.jpg" for index in range(20)]
            for name in sharp_names:
                self._write_image(sharp_dir, name)
            for name in blur_names:
                self._write_image(blurry_dir, name)
            metrics = Path(temporary) / "metrics.csv"
            self._write_metrics(metrics, blur_names)

            destination = Path(temporary) / "view"
            summary = build_view(root, metrics, destination, seed="fixed-seed")

            selected_blur = sorted(
                path.name
                for split in ("train", "val")
                for path in (destination / split / "noisy").iterdir()
            )
            self.assertEqual(selected_blur, [f"b{index:02d}.jpg" for index in range(5, 15)])
            self.assertEqual(summary["counts"]["train"]["clean"], 18)
            self.assertEqual(summary["counts"]["val"]["clean"], 2)
            self.assertEqual(summary["counts"]["train"]["noisy"], 8)
            self.assertEqual(summary["counts"]["val"]["noisy"], 2)
            linked = destination / "train" / "clean" / "s00.jpg"
            self.assertTrue(os.path.samefile(linked, sharp_dir / "s00.jpg"))

    def test_build_view_refuses_to_overwrite_an_existing_destination(self) -> None:
        """Would fail if a later invocation silently mixes or replaces a prior view."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            sharp_dir = root / "Kept_High_Score(Sharp)"
            blurry_dir = root / "Kept_Low_Score(Blurry)"
            sharp_dir.mkdir(parents=True)
            blurry_dir.mkdir(parents=True)
            sharp_name = "s00.jpg"
            blur_names = [f"b{index:02d}.jpg" for index in range(4)]
            self._write_image(sharp_dir, sharp_name)
            for name in blur_names:
                self._write_image(blurry_dir, name)
            metrics = Path(temporary) / "metrics.csv"
            self._write_metrics(metrics, blur_names)
            destination = Path(temporary) / "view"

            build_view(root, metrics, destination, seed="fixed-seed")
            with self.assertRaises(FileExistsError):
                build_view(root, metrics, destination, seed="fixed-seed")


if __name__ == "__main__":
    unittest.main()
