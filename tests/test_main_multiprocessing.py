import sys
import unittest

from omegaconf import OmegaConf

from ddm4ip import main


@unittest.skipUnless(sys.platform == "win32", "Windows regression")
class MultiprocessingStartMethodTests(unittest.TestCase):
    def test_windows_entry_reaches_trainer_dispatch(self):
        cfg = OmegaConf.create({"models": {}, "training": {"train": True}})

        try:
            main.my_app.__wrapped__(cfg)
        except RuntimeError as exc:
            self.assertIn("known trainer", str(exc))
        except ValueError as exc:
            self.fail(f"Entry requested an unsupported start method: {exc}")
        else:
            self.fail("Expected trainer dispatch to reject an empty model config")


if __name__ == "__main__":
    unittest.main()
