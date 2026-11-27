"""Build and dependency checks in the selected project's execution image."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from lab import MakeProfile, save, scan, validate


E3_PROJECT_DIR = Path('E3/cases/mdfixer-target/fixture')
E3_PROFILE = MakeProfile(
    name='b08-e3-target',
    sources=(('build/main.o', 'src/main.c'),),
    allowed_flags=('-Iinclude -Wall -Wextra -O2',),
    include_cppflags=True,
    file_patterns=('src/*.c', 'include/*.h'),
    make_target='all',
    executable='./bin/demo',
    expected_output='10',
    changed_output='11',
    header='include/config.h',
    header_before='#define CONFIG_VALUE 4\n',
    header_after='#define CONFIG_VALUE 5\n',
)


def project_operation(action, project, output, extra=None, *, profile):
    if action == 'full':
        from buildchecker.fullcheck import full_check

        return full_check(project, output, build_command=f'make {profile.make_target}')
    if action == 'scan':
        old = json.loads(extra.read_text()) if extra is not None else None
        result = scan(project, old, profile=profile)
        save(output, result)
        return result
    if action == 'validate':
        return validate(project, extra, output, profile=profile)
    raise ValueError(f'Unknown project operation: {action}')


class ProjectRuntime:
    def __init__(self, profile, logs, image_id=None):
        self.profile = profile
        self.logs = logs
        self.image_id = image_id

    def run(self, action, project, output, extra=None):
        if self.image_id is None:
            return project_operation(action, project, output, extra, profile=self.profile)
        host = Path(os.environ['E11E12_HOST_ROOT'])
        if not host.is_absolute() or not re.fullmatch(r'sha256:[0-9a-f]{64}', self.image_id):
            raise ValueError('INVALID_EXECUTION_IMAGE')
        command = [
            'docker', 'run', '--rm', '--network', 'none', '--cap-add', 'SYS_PTRACE',
            '--user', f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp',
            '-e', 'PYTHONDONTWRITEBYTECODE=1',
            '-e', 'PYTHONPATH=/course/labs/e8e10:/course/labs/e11e12/environment/services/buildchecker',
            '-v', f'{host / "labs"}:/course/labs:ro', '-v', f'{host / "work"}:/course/work',
            '-w', '/course', self.image_id, 'python3', 'labs/e11e12/project_runtime.py',
            action, str(project), str(output),
        ]
        if extra is not None:
            command.append(str(extra))
        log = self.logs / f'{output.name}-runtime.json'
        save(log, {'image_id': self.image_id, 'command': command})
        result = subprocess.run(command, capture_output=True, text=True, timeout=150)
        save(log, {
            'image_id': self.image_id, 'command': command, 'exit_code': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr,
        })
        if result.returncode:
            raise ValueError(f'PROJECT_RUNTIME_FAILED {output.name}; see {log.name}')
        if action == 'full':
            output = output / 'findings.json'
        elif action == 'validate':
            output = output / 'validation.json'
        return json.loads(output.read_text())


if __name__ == '__main__':
    action, project, output, *extra = sys.argv[1:]
    project_operation(action, Path(project), Path(output),
                      Path(extra[0]) if extra else None, profile=E3_PROFILE)
