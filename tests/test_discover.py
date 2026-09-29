import json

import discover


def test_writes_report_into_target_root(workdir):
    (workdir / "pyproject.toml").touch()
    assert discover.main(["--root", str(workdir)]) == 0

    report = json.loads((workdir / "discovery/project.json").read_text())
    assert report["root"] == str(workdir)
    assert report["facts"]["python"]["value"] is True
    assert report["facts"]["node"]["value"] is False


def test_creates_discovery_dir_when_absent(workdir):
    assert not (workdir / "discovery").exists()
    discover.main(["--root", str(workdir)])
    assert (workdir / "discovery/project.json").is_file()


def test_runs_against_foreign_root_from_any_cwd(workdir, tmp_path_factory):
    target = tmp_path_factory.mktemp("foreign")
    (target / "package.json").write_text("{}")

    assert discover.main(["--root", str(target)]) == 0
    report = json.loads((target / "discovery/project.json").read_text())
    assert report["facts"]["node"]["value"] is True
    assert not (workdir / "discovery").exists()


def test_detects_dotnet_via_glob(workdir):
    (workdir / "App.csproj").touch()
    discover.main(["--root", str(workdir)])
    report = json.loads((workdir / "discovery/project.json").read_text())
    assert report["facts"]["dotnet"]["value"] is True


def test_unknowns_are_populated(workdir):
    discover.main(["--root", str(workdir)])
    report = json.loads((workdir / "discovery/project.json").read_text())
    assert "security-boundaries-and-authz-model" in report["unknowns"]
    assert "primary-language-and-stack" in report["unknowns"]
    assert "version-control-history" in report["unknowns"]


def test_stack_detected_removes_stack_unknown(workdir):
    (workdir / "go.mod").touch()
    discover.main(["--root", str(workdir)])
    report = json.loads((workdir / "discovery/project.json").read_text())
    assert "primary-language-and-stack" not in report["unknowns"]


def test_stdout_mode_writes_nothing(workdir, capsys):
    assert discover.main(["--root", str(workdir), "--stdout"]) == 0
    json.loads(capsys.readouterr().out)
    assert not (workdir / "discovery").exists()


def test_default_root_does_not_expose_absolute_path(workdir):
    assert discover.main([]) == 0
    report = json.loads((workdir / "discovery/project.json").read_text())
    assert report["root"] == "."


def test_missing_root_errors(workdir, capsys):
    assert discover.main(["--root", str(workdir / "nope")]) == 1
    assert "not a directory" in capsys.readouterr().err


def test_custom_output_path(workdir):
    out = workdir / "custom/report.json"
    assert discover.main(["--root", str(workdir), "--output", str(out)]) == 0
    assert out.is_file()


def test_git_repo_without_commits_has_null_sha(workdir):
    import subprocess

    subprocess.run(["git", "init", "-q", str(workdir)], check=True)
    discover.main(["--root", str(workdir)])
    report = json.loads((workdir / "discovery/project.json").read_text())
    assert report["facts"]["git"]["value"] is True
    assert report["commit_sha"] is None
    assert "version-control-history" in report["unknowns"]
