import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from pipeline import ROOT, save
from server import Store


class Student241250007Contracts(unittest.TestCase):
    def test_restart_preserves_completed_job_and_marks_interrupted_job(self):
        request = {
            "mode": "e12",
            "repo": str(ROOT / "data" / "student-fixture"),
            "base": "a" * 40,
            "target": "b" * 40,
        }
        request_hash = hashlib.sha256(
            json.dumps(request, sort_keys=True).encode()
        ).hexdigest()

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for suffix, status in (("completed", "SUCCEEDED"), ("running", "RUNNING"),
                                   ("queued", "QUEUED")):
                state = {
                    "job_id": f"job-{suffix}",
                    "idempotency_key": suffix,
                    "request_hash": request_hash,
                    "status": status,
                }
                if status == "SUCCEEDED":
                    state["trace_id"] = "trace-completed"
                save(root / state["job_id"] / "state.json", state)

            store = Store(root)
            try:
                completed = store.submit(request, "completed")
                self.assertEqual(completed["status"], "SUCCEEDED")
                self.assertEqual(completed["job_id"], "job-completed")
                self.assertEqual(completed["trace_id"], "trace-completed")
                for suffix in ("running", "queued"):
                    with self.subTest(status=suffix):
                        interrupted = store.submit(request, suffix)
                        self.assertEqual(interrupted["job_id"], f"job-{suffix}")
                        self.assertEqual(interrupted["status"], "FAILED")
                        self.assertEqual(interrupted["error"]["code"], "SERVER_RESTARTED")
                        persisted = root / interrupted["job_id"] / "state.json"
                        self.assertEqual(json.loads(persisted.read_text()), interrupted)
            finally:
                store.pool.shutdown()
