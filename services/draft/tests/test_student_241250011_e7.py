import json
from pathlib import Path
from types import SimpleNamespace

from draft import autobuild as workflow


def test_zyl_e7_inspect_failure_stops_runtime(tmp_path, monkeypatch):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    base = (
        "FROM python:3.13-slim\n"
        "WORKDIR /work\n"
        "COPY main.c Makefile ./\n"
        "RUN make\n"
        'CMD ["./hello"]\n'
    )
    (fixture / "Dockerfile.broken").write_text(base, encoding="utf-8")
    candidate = tmp_path / "candidate.Dockerfile"
    pinned = "FROM python:3.13-slim@sha256:" + "a" * 64
    candidate.write_text(
        base.replace("FROM python:3.13-slim", pinned).replace(
            "RUN make\n", "RUN apt-get install -y build-essential\nRUN make\n"
        ),
        encoding="utf-8",
    )
    calls = []

    def fake_execute(command, stdout, stderr, timeout):
        calls.append(command)
        Path(stdout).write_text("", encoding="utf-8")
        Path(stderr).write_text("", encoding="utf-8")
        if command[1] == "build":
            if Path(stdout).parent.name == "iter-01":
                Path(stderr).write_text(
                    "/bin/sh: 1: make: not found\n", encoding="utf-8"
                )
                return 1
            return 0
        if command[1:3] == ["image", "inspect"]:
            Path(stderr).write_text(
                "simulated inspect failure\n", encoding="utf-8"
            )
            return 1
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(workflow, "os", SimpleNamespace(name="posix"))
    monkeypatch.setattr(workflow, "execute", fake_execute)

    output = tmp_path / "output"
    report = workflow.auto_build(fixture, candidate, output, "hello E3")

    assert report["status"] == "FAILED"
    assert report["error"] == "Cannot inspect built image"
    assert [a["build_exit_code"] for a in report["attempts"]] == [1, 0]
    assert "verification" not in report
    assert not any(command[1] == "run" for command in calls)
    assert json.loads(
        (output / "result.json").read_text(encoding="utf-8")
    ) == report
    assert (
        output / "iter-02/inspect-stderr.log"
    ).read_text(encoding="utf-8") == "simulated inspect failure\n"
