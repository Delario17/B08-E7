import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pipeline
import server


class Student241250078ContractTests(unittest.TestCase):
    def test_idempotency_binding_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            jobs = Path(directory) / "jobs"
            request = {
                "mode": "e12",
                "repo": str(pipeline.ROOT / "data" / "integration-sample" / "repo"),
                "base": "a" * 40,
                "target": "b" * 40,
            }

            first_store = server.Store(jobs)
            with patch.object(first_store.pool, "submit"):
                first = first_store.submit(request, "241250078-restart-key")
            first_store.pool.shutdown()

            restored_store = server.Store(jobs)
            try:
                reordered = dict(reversed(list(request.items())))
                with patch.object(restored_store.pool, "submit"):
                    replay = restored_store.submit(
                        reordered, "241250078-restart-key"
                    )
                    self.assertEqual(replay["job_id"], first["job_id"])
                    self.assertEqual(len(restored_store.jobs), 1)

                    changed = dict(request, target="c" * 40)
                    with self.assertRaisesRegex(
                        ValueError, "^IDEMPOTENCY_CONFLICT$"
                    ):
                        restored_store.submit(
                            changed, "241250078-restart-key"
                        )
                    self.assertEqual(len(restored_store.jobs), 1)
            finally:
                restored_store.pool.shutdown()


if __name__ == "__main__":
    unittest.main()
