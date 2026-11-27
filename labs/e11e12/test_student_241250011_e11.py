import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch as mock_patch

import pipeline
from lab import fixture, commit, scan, patch, validate


class Student241250011E11Tests(unittest.TestCase):
    def test_mixed_double_md_preserves_variable_and_recipes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "sample"
            fixture(project, "mixed")

            source = project / "main.c"
            source.write_text('#include "extra.h"\n' + source.read_text())
            target = commit(project, "add second missing header")

            before = (project / "Makefile").read_text()
            report = scan(project)
            self.assertEqual(report["commit"], target)

            diff, edits = patch(project, report)
            self.assertEqual((project / "Makefile").read_text(), before)
            self.assertEqual(
                {(e["target"], e["dependency"], e["style"]) for e in edits},
                {
                    ("main.o", "config.h", "mixed"),
                    ("main.o", "extra.h", "mixed"),
                },
            )

            candidate = root / "candidate.patch"
            candidate.write_text(diff)
            result = validate(project, candidate, root / "validation")

            self.assertTrue(result["accepted"])
            self.assertTrue(all(result["checks"].values()))

            after = (project / "Makefile").read_text()
            self.assertIn("HEADERS = unused.h\n", after)
            self.assertIn(
                "main.o: main.c $(HEADERS) config.h extra.h\n", after
            )
            self.assertEqual(
                [line for line in before.splitlines()
                 if line.startswith("\t")],
                [line for line in after.splitlines()
                 if line.startswith("\t")],
            )
            self.assertEqual(
                {(f["type"], f["target"], f["dependency"])
                 for f in scan(project)["findings"]},
                {("REDUNDANT", "main.o", "unused.h")},
            )

    def test_stale_outer_commit_stops_before_repair(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "sample"
            fixture(project)
            report = scan(project)
            target = report["commit"]

            fixed = root / "fixed.json"
            fixed.write_text(json.dumps({
                "schema_version": "e11e12-1",
                "kind": "fixed-md",
                "status": "SUCCEEDED",
                "commit": "0" * 40,
                "data": report,
            }))

            before = {
                p.name: p.read_bytes()
                for p in project.iterdir() if p.is_file()
            }

            def fake_build(source, candidate, output,
                           expected_output, timeout):
                output.mkdir(parents=True)
                result = {"status": "SUCCEEDED"}
                (output / "result.json").write_text(json.dumps(result))
                return result

            request = {
                "mode": "e11-b",
                "repo": str(project),
                "base": target,
                "target": target,
                "candidate": str(root / "candidate"),
                "fixed_report": str(fixed),
                "expected_output": "1",
            }

            with mock_patch(
                "draft.autobuild.auto_build", side_effect=fake_build
            ), mock_patch.object(
                pipeline, "patch"
            ) as repair, mock_patch.object(
                pipeline.ProjectRuntime, "run"
            ) as runtime:
                result = pipeline.execute(request, root / "output")

            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["error"]["code"], "STALE_REPORT")
            self.assertEqual(
                [s["name"] for s in result["stages"]], ["draft"]
            )
            repair.assert_not_called()
            runtime.assert_not_called()
            self.assertFalse((root / "output/candidate.patch").exists())
            self.assertEqual(
                {
                    p.name: p.read_bytes()
                    for p in project.iterdir() if p.is_file()
                },
                before,
            )


if __name__ == "__main__":
    unittest.main()
