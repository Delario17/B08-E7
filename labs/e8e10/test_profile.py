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
class Student241250011Tests(unittest.TestCase):
    def test_e8_unknown_target_preserves_source(self):
        from lab import run

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "sample"
            fixture(project)
            report = scan(project)
            report["findings"] = [
                {"type": "MISSING", "target": "unknown.o", "dependency": "config.h"}
            ]
            before = (project / "Makefile").read_bytes()

            with self.assertRaisesRegex(ValueError, "^UNSUPPORTED_TARGET$"):
                patch(project, report)

            self.assertEqual((project / "Makefile").read_bytes(), before)
            self.assertEqual(
                run(["git", "status", "--porcelain"], project).strip(), ""
            )

    def test_e9_macro_patch_preserves_reference_and_rechecks(self):
        from lab import run

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "sample"
            fixture(project, "macro")
            before = (project / "Makefile").read_bytes()

            diff, edits = patch(project, scan(project))
            self.assertEqual(edits, [
                {"target": "main.o", "dependency": "config.h", "style": "macro"}
            ])
            self.assertEqual((project / "Makefile").read_bytes(), before)

            candidate = Path(directory) / "candidate.patch"
            candidate.write_text(diff)
            run(["git", "apply", str(candidate.resolve())], project)

            lines = (project / "Makefile").read_text().splitlines()
            self.assertIn("DEPS = main.c unused.h config.h", lines)
            self.assertIn("main.o: $(DEPS)", lines)
            self.assertEqual(scan(project)["findings"], [
                {"type": "REDUNDANT", "target": "main.o", "dependency": "unused.h"}
            ])


class Student241250078Tests(unittest.TestCase):
    def test_e8_stale_report_preserves_project_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "sample"
            fixture(project)
            report = scan(project)
            report["commit"] = "0" * 40
            before = {
                path.name: path.read_bytes()
                for path in project.iterdir() if path.is_file()
            }

            with self.assertRaisesRegex(ValueError, "^STALE_REPORT$"):
                patch(project, report)

            after = {
                path.name: path.read_bytes()
                for path in project.iterdir() if path.is_file()
            }
            self.assertEqual(after, before)

    def test_e9_direct_patch_preserves_recipe_bytes(self):
        from lab import run

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "sample"
            fixture(project, "direct")
            makefile = project / "Makefile"
            before = makefile.read_bytes()
            diff, edits = patch(project, scan(project))

            self.assertEqual(edits, [{
                "target": "main.o",
                "dependency": "config.h",
                "style": "direct",
            }])
            self.assertEqual(makefile.read_bytes(), before)

            candidate = Path(directory) / "candidate.patch"
            candidate.write_text(diff)
            run(["git", "apply", str(candidate.resolve())], project)
            after = makefile.read_bytes()

            recipes = lambda content: [
                line for line in content.splitlines() if line.startswith(b"\t")
            ]
            self.assertEqual(recipes(after), recipes(before))
            self.assertIn(b"main.o: main.c unused.h config.h", after)

    def test_e10_compile_failure_rolls_back_source(self):
        from lab import validate

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "sample"
            fixture(project)
            (project / "main.c").write_text(
                '#include "config.h"\nint main(void) { invalid C; }\n'
            )
            commit(project, "introduce compile failure")
            candidate = root / "candidate.patch"
            candidate.write_text(patch(project, scan(project))[0])
            before = (project / "Makefile").read_bytes()

            result = validate(project, candidate, root / "validation")

            self.assertFalse(result["accepted"])
            self.assertTrue(result["checks"]["patch_applies"])
            self.assertNotIn("build", result["checks"])
            self.assertIn("COMMAND_FAILED", result["error"])
            self.assertTrue(result["rollback"])
            self.assertTrue(result["source_unchanged"])
            self.assertEqual((project / "Makefile").read_bytes(), before)


class Student241250008E10Tests(unittest.TestCase):
    def test_buildable_candidate_with_missing_dependency_is_rejected(self):
        import difflib
        from lab import run, validate

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'sample'
            fixture(project)
            before = {path.name: path.read_bytes()
                      for path in project.iterdir() if path.is_file()}
            original = before['Makefile'].decode()
            changed = original.replace('CFLAGS = -O0', 'CFLAGS = -O1')
            candidate = root / 'remaining-md.patch'
            candidate.write_text(''.join(difflib.unified_diff(
                original.splitlines(True), changed.splitlines(True),
                fromfile='a/Makefile', tofile='b/Makefile'
            )))

            evidence = root / 'validation'
            result = validate(project, candidate, evidence)
            self.assertEqual(result['checks'], {
                'patch_applies': True, 'build': True, 'test': True,
                'header_change': False, 'no_missing': False,
            })
            self.assertIsNone(result['error'])
            self.assertFalse(result['accepted'])
            self.assertTrue(result['rollback'])
            self.assertTrue(result['source_unchanged'])
            after = {path.name: path.read_bytes()
                     for path in project.iterdir() if path.is_file()}
            self.assertEqual(after, before)
            self.assertEqual(run(['git', 'status', '--porcelain'], project), '')
            recheck = json.loads((evidence / 'recheck.json').read_text())
            missing = {(f['target'], f['dependency'])
                       for f in recheck['findings'] if f['type'] == 'MISSING'}
            self.assertEqual(missing, {('main.o', 'config.h')})
            self.assertEqual(run(['./app'], evidence / 'sandbox').strip(), '1')
            self.assertIn('VALUE 2', (evidence / 'sandbox/config.h').read_text())
            self.assertEqual(json.loads((evidence / 'validation.json').read_text()),
                             result)

if __name__=='__main__':unittest.main()
