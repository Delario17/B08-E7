import pytest

from draft.autobuild import prepare_candidate


def test_rejects_candidate_with_second_from():
    base = "m.daocloud.io/docker.io/library/python:3.13-slim"
    pinned = f"{base}@sha256:{'a' * 64}"
    original = (
        f"FROM {base}\n"
        "WORKDIR /work\n"
        "COPY main.c Makefile ./\n"
        "RUN make\n"
        'CMD ["./hello"]\n'
    )
    valid_candidate = original.replace(
        f"FROM {base}\n", f"FROM {pinned}\n", 1
    ).replace(
        "RUN make\n",
        "RUN apt-get install -y make gcc libc6-dev\nRUN make\n",
        1,
    )

    # 先确认对照候选能通过，再只加入一条 FROM。
    prepare_candidate(original, valid_candidate)
    multistage = valid_candidate.replace(
        "WORKDIR /work\n",
        f"FROM {pinned}\nWORKDIR /work\n",
        1,
    )

    with pytest.raises(ValueError, match="Only single-stage candidates are supported"):
        prepare_candidate(original, multistage)
