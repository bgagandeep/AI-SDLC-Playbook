import io
import json

import test_guard


def hook_event(path):
    return json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(path)}})


def test_lock_blocks_edit_to_exact_file(workdir, monkeypatch, capsys):
    test_file = workdir / "tests/test_feature.py"
    test_file.parent.mkdir()
    test_file.touch()
    assert test_guard.main(["lock", str(test_file)]) == 0

    monkeypatch.setattr("sys.stdin", io.StringIO(hook_event(test_file)))
    assert test_guard.main(["check-hook"]) == 2
    assert "BLOCKED" in capsys.readouterr().err


def test_lock_directory_blocks_descendant(workdir, monkeypatch):
    tests = workdir / "tests"
    tests.mkdir()
    assert test_guard.main(["lock", str(tests)]) == 0

    monkeypatch.setattr("sys.stdin", io.StringIO(hook_event(tests / "unit/test_api.py")))
    assert test_guard.main(["check-hook"]) == 2


def test_unrelated_source_edit_passes(workdir, monkeypatch):
    test_file = workdir / "tests/test_feature.py"
    test_file.parent.mkdir()
    test_file.touch()
    test_guard.main(["lock", str(test_file)])

    monkeypatch.setattr("sys.stdin", io.StringIO(hook_event(workdir / "src/feature.py")))
    assert test_guard.main(["check-hook"]) == 0


def test_unlock_all_removes_guard(workdir, monkeypatch):
    test_file = workdir / "tests/test_feature.py"
    test_file.parent.mkdir()
    test_file.touch()
    test_guard.main(["lock", str(test_file)])
    assert test_guard.main(["unlock", "--all"]) == 0

    monkeypatch.setattr("sys.stdin", io.StringIO(hook_event(test_file)))
    assert test_guard.main(["check-hook"]) == 0


def test_missing_path_cannot_be_locked(workdir, capsys):
    assert test_guard.main(["lock", "tests/missing.py"]) == 1
    assert "missing path" in capsys.readouterr().err


def test_unlock_requires_selection(workdir, capsys):
    assert test_guard.main(["unlock"]) == 1
    assert "provide paths or --all" in capsys.readouterr().err


def test_malformed_hook_event_blocks_when_guard_active(workdir, monkeypatch, capsys):
    tests = workdir / "tests"
    tests.mkdir()
    test_guard.main(["lock", str(tests)])
    monkeypatch.setattr("sys.stdin", io.StringIO("not-json"))
    assert test_guard.main(["check-hook"]) == 2
    assert "could not parse" in capsys.readouterr().err


def test_corrupt_state_fails_closed(workdir, capsys):
    state = workdir / ".agent/test-lock.json"
    state.parent.mkdir()
    state.write_text("{broken")
    assert test_guard.main(["status"]) == 1
    assert "corrupt" in capsys.readouterr().err
