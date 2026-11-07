"""Student 241250078 E7 boundary: classify an alternate shell message."""

from draft.autobuild import classify_failure


def test_241250078_make_command_not_found_is_missing_make():
    log = "/bin/sh: 1: make: command not found"

    assert classify_failure(log) == "MISSING_MAKE"
