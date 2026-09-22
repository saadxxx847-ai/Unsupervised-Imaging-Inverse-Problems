import json
import subprocess
import tempfile
import unittest
from pathlib import Path

WRAPPER = Path(r"D:\DDM4IP-runtime\orchestration\step1_resume_watchdog.ps1")
TEMP = Path(r"D:\DDM4IP-runtime\temp")

class RecoverySafetyTests(unittest.TestCase):
    def check_guard(self, status, dry_run):
        root = Path(tempfile.mkdtemp(prefix="step1-recovery-safety-", dir=TEMP))
        print("Retained recovery fixture:", root)
        marker = root / "stage-executed.txt"
        stub = root / "stub-stage.ps1"
        stub.write_text("Set-Content -LiteralPath '" + str(marker) + "' -Value invoked\nexit 0\n")
        wrapper = root / "watchdog.ps1"
        wrapper.write_text(WRAPPER.read_text(encoding="utf-8-sig").replace(
            r"D:\DDM4IP-runtime\orchestration\run_bdd100k_synthetic_stage.ps1", str(stub)), encoding="utf-8")
        spec = root / "spec.json"
        spec.write_text(json.dumps({"run_root": str(root), "stage": "step1", "mode": "full"}))
        state = root / "status.json"
        state.write_text(json.dumps({"status": status}))
        claim = root / "execution.claim"
        claim.write_bytes(b"historical claim\n")
        command = ["powershell.exe", "-NoProfile", "-NonInteractive", "-File", str(wrapper),
                   "-RunRoot", str(root), "-ReservedSpec", str(spec)]
        if dry_run:
            command.append("-DryRun")
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(claim.exists(), "recovery must preserve execution.claim")
        self.assertEqual(claim.read_bytes(), b"historical claim\n")
        self.assertFalse(list(root.glob("execution.claim.stale-*")))
        self.assertFalse(marker.exists(), "guard must not execute the training wrapper")
        self.assertEqual(json.loads(state.read_text()), {"status": status})

    def test_dry_run_preserves_running_claim(self):
        self.check_guard("RUNNING", True)

    def test_failed_run_is_not_reexecuted(self):
        self.check_guard("FAILED", False)

    def test_success_run_is_not_reexecuted(self):
        self.check_guard("SUCCESS", False)

if __name__ == "__main__":
    unittest.main()
