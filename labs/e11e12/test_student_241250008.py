import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch as mock_patch

import pipeline
from lab import commit, fixture, patch, run, scan


class Student241250008E11Tests(unittest.TestCase):
    def test_macro_repairs_both_missing_headers_and_preserves_recipes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'sample'
            fixture(project, 'macro')
            source = project / 'main.c'
            source.write_text('#include "extra.h"\n' + source.read_text())
            commit(project, 'student: introduce second missing header')
            before = (project / 'Makefile').read_bytes()
            diff, edits = patch(project, scan(project))
            self.assertEqual(edits, [
                {'target': 'main.o', 'dependency': 'config.h', 'style': 'macro'},
                {'target': 'main.o', 'dependency': 'extra.h', 'style': 'macro'},
            ])
            self.assertEqual((project / 'Makefile').read_bytes(), before)
            candidate = root / 'candidate.patch'
            candidate.write_text(diff)
            run(['git', 'apply', '--check', str(candidate)], project)
            run(['git', 'apply', str(candidate)], project)
            after = (project / 'Makefile').read_bytes()
            self.assertIn(b'DEPS = main.c unused.h config.h extra.h', after)
            self.assertIn(b'main.o: $(DEPS)', after)
            self.assertEqual(
                [line for line in before.splitlines() if line.startswith(b'\t')],
                [line for line in after.splitlines() if line.startswith(b'\t')],
            )
            self.assertEqual(
                {(f['type'], f['target'], f['dependency'])
                 for f in scan(project)['findings']},
                {('REDUNDANT', 'main.o', 'unused.h')},
            )

    def test_stale_embedded_commit_stops_before_repair(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'sample'
            fixture(project)
            report = scan(project)
            target = report['commit']
            report['commit'] = '0' * 40
            fixed = root / 'fixed.json'
            fixed.write_text(json.dumps({
                'schema_version': 'e11e12-1', 'kind': 'fixed-md',
                'status': 'SUCCEEDED', 'commit': target, 'data': report,
            }))
            before = {p.name: p.read_bytes()
                      for p in project.iterdir() if p.is_file()}

            def fake_build(source, candidate, output, expected_output, timeout):
                output.mkdir()
                result = {'status': 'SUCCEEDED'}
                (output / 'result.json').write_text(json.dumps(result))
                return result

            request = {'mode': 'e11-b', 'repo': str(project), 'base': target,
                       'target': target, 'candidate': str(root / 'candidate'),
                       'fixed_report': str(fixed), 'expected_output': '1'}
            with mock_patch('draft.autobuild.auto_build', side_effect=fake_build), \
                    mock_patch.object(pipeline, 'patch') as repair, \
                    mock_patch.object(pipeline.ProjectRuntime, 'run') as runtime:
                result = pipeline.execute(request, root / 'output')
            self.assertEqual(result['status'], 'FAILED')
            self.assertEqual(result['error']['code'], 'STALE_REPORT')
            self.assertEqual([s['name'] for s in result['stages']], ['draft'])
            repair.assert_not_called()
            runtime.assert_not_called()
            self.assertFalse((root / 'output/candidate.patch').exists())
            self.assertEqual(before, {p.name: p.read_bytes()
                                     for p in project.iterdir() if p.is_file()})


if __name__ == '__main__':
    unittest.main()
