import tempfile
import unittest
from pathlib import Path

from pipeline import snapshot
from lab import commit, declarations, run
from prepare_b08_e3 import CANDIDATE, add_target
from project_runtime import E3_PROFILE, E3_PROJECT_DIR
from draft.autobuild import prepare_candidate


class B08E3IntegrationTests(unittest.TestCase):
    def test_native_layout_and_new_target_keep_declared_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / 'upstream'
            project = repository / E3_PROJECT_DIR
            (project / 'src').mkdir(parents=True)
            (project / 'include').mkdir()
            (repository / 'unrelated.txt').write_text('outside the selected project\n')
            (project / 'src/main.c').write_text(
                '#include "config.h"\nint main(void) { puts("demo 1.0.0"); }\n'
            )
            (project / 'include/config.h').write_text('#define CONFIG_VALUE 4\n')
            makefile = (
                'CPPFLAGS := -Iinclude\nCFLAGS := -Wall -Wextra -O2\n'
                'build/main.o: src/main.c include/common.h\n'
            )
            (project / 'Makefile').write_text(makefile)
            run(['git', 'init', '-b', 'main'], repository)
            run(['git', 'config', 'user.name', 'Fixture'], repository)
            run(['git', 'config', 'user.email', 'fixture@localhost'], repository)
            base = commit(repository, 'Prior project layout')

            add_target(project)
            target = commit(repository, 'Version header')
            self.assertNotEqual(base, target)
            self.assertEqual(run(['git', 'rev-parse', 'HEAD^'], repository).strip(), base)
            self.assertEqual((project / 'Makefile').read_text(), makefile)
            self.assertIn('#include "version.h"', (project / 'src/main.c').read_text())
            self.assertIn('"1.1.0"', (project / 'include/version.h').read_text())
            baseline = prepare_candidate((project / 'Dockerfile.broken').read_text(), CANDIDATE)
            self.assertIn('RUN make all', baseline)
            self.assertNotIn('apt-get', baseline)
            self.assertIn('make git strace', CANDIDATE)

            sha, checkout = snapshot(repository, target, root / 'target', root / 'logs',
                                     E3_PROFILE, E3_PROJECT_DIR)
            self.assertEqual(target, sha)
            self.assertFalse((root / 'target/unrelated.txt').exists())
            self.assertEqual(declarations(checkout, E3_PROFILE), (
                {'build/main.o': ['include/common.h', 'src/main.c']},
                '-Iinclude -Wall -Wextra -O2',
            ))
