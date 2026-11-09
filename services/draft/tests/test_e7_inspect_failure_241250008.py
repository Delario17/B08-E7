"""Check that an uninspectable repair image never reaches program execution."""
import json
from pathlib import Path

from draft import autobuild as workflow


def test_image_inspect_failure_stops_program_verification(tmp_path, monkeypatch):
    original = (
        "FROM python:3.13-slim\n"
        "WORKDIR /work\n"
        "COPY main.c Makefile ./\n"
        "RUN make\n"
        'CMD ["./hello"]\n'
    )
    candidate_text = original.replace(
        "FROM python:3.13-slim", "FROM python:3.13-slim@sha256:" + "a" * 64
    ).replace("RUN make", "RUN apt-get install -y build-essential\nRUN make")
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    (fixture / "Dockerfile.broken").write_text(original, encoding="utf-8")
    (fixture / "main.c").write_text("int main(void) { return 0; }\n")
    (fixture / "Makefile").write_text("hello:\n\tcc main.c -o hello\n")
    candidate = tmp_path / "candidate.Dockerfile"
    candidate.write_text(candidate_text, encoding="utf-8")
    calls = []

    def fake_execute(argv, stdout, stderr, timeout):
        calls.append(argv)
        stdout, stderr = Path(stdout), Path(stderr)
        stdout.write_text("", encoding="utf-8")
        stderr.write_text("", encoding="utf-8")
        if argv[1] == "build":
            if stdout.parent.name == "iter-01":
                stderr.write_text("/bin/sh: 1: make: not found\n")
                return 1
            return 0
        if argv[1:3] == ["image", "inspect"]:
            stderr.write_text("Error response from daemon: No such image\n")
            return 1
        raise AssertionError(f"Unexpected Docker operation after inspect failure: {argv}")

    monkeypatch.setattr(workflow, "execute", fake_execute)
    output = tmp_path / "output"
    report = workflow.auto_build(fixture, candidate, output, "hello E3")

    assert report["status"] == "FAILED"
    assert report["error"] == "Cannot inspect built image"
    assert len(report["attempts"]) == 2
    assert report["attempts"][0]["failure_class"] == "MISSING_MAKE"
    assert report["attempts"][1]["build_exit_code"] == 0
    assert "verification" not in report
    assert [command[1] for command in calls] == ["build", "build", "image"]
    assert "No such image" in (output / "iter-02/inspect-stderr.log").read_text()
    assert not (output / "verify.log").exists()
    assert json.loads((output / "result.json").read_text()) == report
