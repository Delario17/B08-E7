"""Prepare a new E12 target on a local clone of B08's versioned E3 project."""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'labs/e8e10'))
from project_runtime import E3_PROFILE, E3_PROJECT_DIR

SOURCE_URL = 'https://github.com/Delario17/DevOps-Course-Assignment.git'
BASE_COMMIT = 'c9c8aead2c1cede2b6d0e66f4c74604b8d64ca0b'
BASE_TAG = 'm.daocloud.io/docker.io/library/python:3.13-slim'
BASE_DIGEST = 'sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f'
BROKEN = f"""FROM {BASE_TAG}
WORKDIR /work
COPY Makefile ./
COPY include/ include/
COPY src/ src/
RUN make all
CMD ["./bin/demo"]
"""
CANDIDATE = BROKEN.replace(f'FROM {BASE_TAG}', f'FROM {BASE_TAG}@{BASE_DIGEST}', 1).replace(
    'RUN make all',
    'RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev make git strace'
    ' && rm -rf /var/lib/apt/lists/*\nRUN make all', 1,
)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def add_target(project):
    source = project / 'src/main.c'
    text = source.read_text()
    include = '#include "config.h"'
    version = 'puts("demo 1.0.0");'
    if text.count(include) != 1 or text.count(version) != 1:
        raise ValueError('E3 source does not match the pinned baseline')
    source.write_text(text.replace(include, include + '\n#include "version.h"', 1)
                      .replace(version, 'puts("demo " DEMO_VERSION);', 1))
    (project / 'include/version.h').write_text(
        '#ifndef DEMO_VERSION_H\n#define DEMO_VERSION_H\n'
        '#define DEMO_VERSION "1.1.0"\n#endif\n'
    )
    (project / 'Dockerfile.broken').write_text(BROKEN)


def prepare(source, destination):
    if destination.exists():
        raise ValueError(f'Choose a fresh destination: {destination}')
    if not destination.is_relative_to(ROOT / 'data') or destination == ROOT / 'data':
        raise ValueError('The project destination must be below data/')
    git(source, 'rev-parse', '--verify', BASE_COMMIT + '^{commit}')
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        staging = Path(temporary) / 'project'
        staging.mkdir()
        repository = staging / 'repo'
        subprocess.run(['git', 'clone', '--no-hardlinks', '--no-checkout', str(source),
                        str(repository)], check=True)
        git(repository, 'sparse-checkout', 'set', '--no-cone', f'/{E3_PROJECT_DIR}/')
        git(repository, 'switch', '-c', 'e12-b08-target', BASE_COMMIT)
        git(repository, 'config', 'user.name', 'B08 E12 Integration')
        git(repository, 'config', 'user.email', 'b08-e12@localhost')
        add_target(repository / E3_PROJECT_DIR)
        git(repository, 'add', '--', str(E3_PROJECT_DIR))
        git(repository, 'commit', '-m', 'E12: version the E3 demo through a project header')
        target = git(repository, 'rev-parse', 'HEAD')

        container_dir = Path('/course') / destination.relative_to(ROOT)
        request = {
            'mode': 'e12',
            'project_profile': E3_PROFILE.name,
            'repo': str(container_dir / 'repo'),
            'base': BASE_COMMIT,
            'target': target,
            'candidate': str(container_dir / 'candidate.Dockerfile'),
            'expected_output': E3_PROFILE.expected_output,
            'build_timeout': 600,
        }
        dataset = {
            'source_repository': SOURCE_URL,
            'source_path': E3_PROJECT_DIR.as_posix(),
            'original_material': 'B08 E3 Target course case derived from A08',
            'base_commit': BASE_COMMIT,
            'target_commit': target,
            'target_provenance': 'New E12 integration commit on an isolated clone',
            'target_change': 'Move --version to include/version.h and add DRAFT inputs',
            'dependency_faults': [
                {'target': 'build/main.o', 'dependency': 'include/config.h', 'origin': 'E3 baseline'},
                {'target': 'build/main.o', 'dependency': 'include/version.h', 'origin': 'E12 exercise'},
            ],
            'expected_output': {'initial': '10', 'after_config_header_change': '11'},
        }
        (staging / 'candidate.Dockerfile').write_text(CANDIDATE)
        for name, record in [('e12.json', request), ('dataset.json', dataset)]:
            (staging / name).write_text(json.dumps(record, indent=2) + '\n')
        staging.rename(destination)

    return request


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path, help='Local B08 course repository')
    parser.add_argument('--out', default=Path('data/real-project'), type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source.resolve(), (ROOT / args.out).resolve()), indent=2))
