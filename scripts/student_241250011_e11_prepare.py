"""Prepare reproducible E11-B direct/mixed inputs for student 241250011."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from lab import fixture, commit, scan

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "e1acb00349a5c3281bf77ff5d61da0ec75ee5f8f"
BASE_TAG = "m.daocloud.io/docker.io/library/python:3.13-slim"
DIGEST = "70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f"


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    root = (ROOT / args.out).resolve()
    if not root.is_relative_to(ROOT / "data") or root == ROOT / "data":
        raise SystemExit("--out must be a new subdirectory of data/")
    if root.exists():
        raise SystemExit("Input directory already exists; preserve it")

    student_source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    email = subprocess.check_output(
        ["git", "config", "--local", "user.email"], cwd=ROOT, text=True
    ).strip()

    for style in ("direct", "mixed"):
        case = root / style
        project = case / "repo"
        fixture(project, style)

        subprocess.run(
            ["git", "config", "user.name", "241250011"],
            cwd=project, check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", email],
            cwd=project, check=True,
        )

        broken = (
            f"FROM {BASE_TAG}\n"
            "WORKDIR /work\n"
            "COPY main.c helper.c config.h extra.h unused.h Makefile ./\n"
            "RUN make app\n"
            'CMD ["./app"]\n'
        )
        (project / "Dockerfile.broken").write_text(broken)
        base = commit(project, f"241250011 {style} C0")

        source = project / "main.c"
        source.write_text('#include "extra.h"\n' + source.read_text())
        target = commit(project, f"241250011 {style} C1 add extra include")

        candidate = broken.replace(
            f"FROM {BASE_TAG}\n",
            f"FROM {BASE_TAG}@sha256:{DIGEST}\n",
            1,
        ).replace(
            "RUN make app\n",
            "RUN apt-get update && apt-get install -y "
            "--no-install-recommends build-essential "
            "&& rm -rf /var/lib/apt/lists/*\n"
            "RUN make app\n",
            1,
        )
        candidate_path = case / "candidate.Dockerfile"
        candidate_path.write_text(candidate)

        report = scan(project)
        assert report["commit"] == target
        assert {
            (f["target"], f["dependency"])
            for f in report["findings"] if f["type"] == "MISSING"
        } == {
            ("main.o", "config.h"),
            ("main.o", "extra.h"),
        }

        fixed_path = case / "fixed-md.json"
        save(fixed_path, {
            "schema_version": "e11e12-1",
            "kind": "fixed-md",
            "status": "SUCCEEDED",
            "commit": target,
            "data": report,
        })

        request = {
            "mode": "e11-b",
            "repo": str(project),
            "base": base,
            "target": target,
            "candidate": str(candidate_path),
            "fixed_report": str(fixed_path),
            "expected_output": "1",
            "build_timeout": 7200,
        }
        save(case / "request.json", request)

        save(case / "dataset.json", {
            "student_id": "241250011",
            "style": style,
            "source": "course-generated controlled C/Make fixture",
            "upstream_pr": "https://github.com/Delario17/B08-E7/pull/14",
            "upstream_commit": UPSTREAM,
            "preparation_source_commit": student_source,
            "base_commit": base,
            "target_commit": target,
            "change": "main.c adds extra.h include",
            "expected_output": "1",
            "candidate_source": (
                "Course recorded dependency-install pattern adapted "
                "to this two-source-file fixture; no model/API call"
            ),
            "network_adaptation": (
                "Dockerfile.broken and candidate use the same mirrored "
                "Python tag; candidate retains the course SHA256 digest"
            ),
            "candidate_sha256": hashlib.sha256(
                candidate.encode("utf-8")
            ).hexdigest(),
        })

        if style == "mixed":
            stale = json.loads(json.dumps({
                "schema_version": "e11e12-1",
                "kind": "fixed-md",
                "status": "SUCCEEDED",
                "commit": target,
                "data": report,
            }))
            stale["data"]["commit"] = "0" * 40
            stale_path = case / "stale-inner-fixed-md.json"
            save(stale_path, stale)

            stale_request = dict(request)
            stale_request["fixed_report"] = str(stale_path)
            save(case / "request-stale-inner.json", stale_request)

        print(style, "base=", base, "target=", target)

    print("INPUT_ROOT=" + str(root))


if __name__ == "__main__":
    main()
