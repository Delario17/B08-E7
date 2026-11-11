import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

class Student241250007Tests(unittest.TestCase):
    def test_e8_redundant_only_produces_no_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'sample'
            fixture(project)
            report = scan(project)
            report['findings'] = [
                f for f in report['findings']
                if f['type'] == 'REDUNDANT'
            ]
            self.assertEqual(len(report['findings']), 1)

            before = (project / 'Makefile').read_bytes()
            diff, edits = patch(project, report)

            self.assertEqual(diff, '')
            self.assertEqual(edits, [])
            self.assertEqual(
                (project / 'Makefile').read_bytes(), before
            )

    def test_e9_mixed_patch_preserves_variable_and_recipes(self):
        from lab import run

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'sample'
            fixture(project, 'mixed')
            before = (project / 'Makefile').read_bytes()

            diff, edits = patch(project, scan(project))
            self.assertEqual(edits[0]['style'], 'mixed')

            candidate = Path(directory) / 'candidate.patch'
            candidate.write_text(diff)
            run([
                'git', 'apply', str(candidate.resolve())
            ], project)

            after = (project / 'Makefile').read_bytes()
            self.assertIn(b'HEADERS = unused.h', after)
            self.assertIn(
                b'main.o: main.c $(HEADERS) config.h', after
            )

            recipes_before = [
                line for line in before.splitlines()
                if line.startswith(b'\t')
            ]
            recipes_after = [
                line for line in after.splitlines()
                if line.startswith(b'\t')
            ]
            self.assertEqual(recipes_before, recipes_after)

class Student241250008E8Tests(unittest.TestCase):
    def test_unknown_target_is_rejected_without_source_changes(self):
        from lab import run

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'sample'
            fixture(project)
            report = scan(project)
            report['findings'] = [{
                'type': 'MISSING',
                'target': 'unknown.o',
                'dependency': 'config.h',
            }]
            before = {
                path.name: path.read_bytes()
                for path in project.iterdir() if path.is_file()
            }

            with self.assertRaisesRegex(ValueError, '^UNSUPPORTED_TARGET$'):
                patch(project, report)

            after = {
                path.name: path.read_bytes()
                for path in project.iterdir() if path.is_file()
            }
            self.assertEqual(after, before)
            self.assertEqual(run(['git', 'status', '--porcelain'], project), '')

class Student241250008E9Tests(unittest.TestCase):
    def test_shared_macro_adds_dependency_to_both_targets(self):
        from lab import run

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'sample'
            fixture(project, 'macro')
            makefile = project / 'Makefile'
            makefile.write_text(makefile.read_text().replace(
                'helper.o: helper.c', 'helper.o: helper.c $(DEPS)'
            ))
            commit(project, 'student: share DEPS across object targets')
            before = makefile.read_bytes()
            initial = scan(project)
            self.assertEqual(initial['declared']['helper.o'],
                             ['helper.c', 'main.c', 'unused.h'])

            diff, edits = patch(project, initial)
            self.assertEqual(edits, [{
                'target': 'main.o', 'dependency': 'config.h', 'style': 'macro'
            }])
            self.assertEqual(makefile.read_bytes(), before)
            candidate = Path(directory) / 'candidate.patch'
            candidate.write_text(diff)
            run(['git', 'apply', '--check', str(candidate.resolve())], project)
            run(['git', 'apply', str(candidate.resolve())], project)

            after = makefile.read_bytes()
            self.assertIn(b'DEPS = main.c unused.h config.h', after)
            self.assertIn(b'main.o: $(DEPS)', after)
            self.assertIn(b'helper.o: helper.c $(DEPS)', after)
            self.assertEqual(
                [line for line in before.splitlines() if line.startswith(b'\t')],
                [line for line in after.splitlines() if line.startswith(b'\t')]
            )
            result = scan(project)
            self.assertEqual(result['declared']['helper.o'],
                             ['config.h', 'helper.c', 'main.c', 'unused.h'])
            findings = {(f['type'], f['target'], f['dependency'])
                        for f in result['findings']}
            self.assertEqual(findings, {
                ('REDUNDANT', 'main.o', 'unused.h'),
                ('REDUNDANT', 'helper.o', 'config.h'),
                ('REDUNDANT', 'helper.o', 'main.c'),
                ('REDUNDANT', 'helper.o', 'unused.h'),
            })

if __name__=='__main__':unittest.main()
