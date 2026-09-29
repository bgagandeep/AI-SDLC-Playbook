"""Structural checks on the framework itself: docs must match the repository."""
import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "AGENTS.md",
    "SPEC.md",
    "PLANNING.md",
    "README.md",
    "LICENSE",
    "project.config.yaml",
    "FRAMEWORK-MANIFEST.json",
    "requirements.txt",
    ".gitignore",
    ".claude/settings.json",
    ".claude/hooks/production-gate.sh",
    ".cursor/hooks.json",
    ".cursor/hooks/grind.ts",
    ".github/workflows/ci.yml",
    ".github/workflows/security.yml",
    ".github/workflows/release-gate.yml",
    "scripts/verify-context-kit.sh",
    "scripts/gate_ledger.py",
    "scripts/org_status.py",
    "scripts/discover.py",
    "scripts/check_governance.py",
    "scripts/test_guard.py",
    "discovery/README.md",
    "intent/README.md",
    "specs/README.md",
    "plans/README.md",
    "docs/governance/release-gates.md",
    "evals/README.md",
    "governance/README.md",
    "incidents/README.md",
    "telemetry/bands.yaml",
]


@pytest.mark.parametrize("relative", REQUIRED_PATHS)
def test_required_path_exists(relative):
    assert (REPO_ROOT / relative).exists(), f"{relative} is referenced by the framework but missing"


@pytest.mark.parametrize("script", ["scripts/verify-context-kit.sh", ".claude/hooks/production-gate.sh"])
def test_shell_scripts_are_executable(script):
    assert (REPO_ROOT / script).stat().st_mode & 0o111, f"{script} is not executable"


@pytest.mark.parametrize("script", ["scripts/verify-context-kit.sh", ".claude/hooks/production-gate.sh"])
def test_shell_scripts_parse(script):
    assert subprocess.run(["bash", "-n", str(REPO_ROOT / script)], check=False).returncode == 0


def test_all_yaml_parses():
    for path in REPO_ROOT.rglob("*.yaml"):
        if "node_modules" in path.parts or ".venv" in path.parts:
            continue
        yaml.safe_load(path.read_text())


def test_all_json_parses():
    for path in REPO_ROOT.rglob("*.json"):
        if "node_modules" in path.parts or "reviews" in path.parts or ".venv" in path.parts:
            continue
        json.loads(path.read_text())


def test_readme_structure_map_matches_repo():
    """Every path drawn in the README tree must actually exist."""
    readme = (REPO_ROOT / "README.md").read_text()
    block = re.search(r"```text\nai-native-sdlc/\n(.*?)```", readme, re.DOTALL)
    assert block, "README repository structure map not found"

    missing = []
    for line in block.group(1).splitlines():
        entry = re.sub(r"^[│├└─\s]+", "", line).split("#")[0].strip()
        if not entry or entry.endswith("/"):
            continue
        matches = list(REPO_ROOT.rglob(entry))
        if not matches:
            missing.append(entry)
    assert not missing, f"README documents nonexistent paths: {missing}"


def test_agents_md_sections_are_sequential():
    content = (REPO_ROOT / "AGENTS.md").read_text()
    numbers = [int(n) for n in re.findall(r"^## (\d+)\.", content, re.MULTILINE)]
    assert numbers == list(range(1, len(numbers) + 1)), f"AGENTS.md section numbering has gaps: {numbers}"


def test_no_placeholder_clone_url():
    assert "your-org" not in (REPO_ROOT / "README.md").read_text()


def test_intent_directory_is_consistent():
    """org/intake/ was a stale alias for intent/."""
    for name in ("AGENTS.md", "README.md", "SPEC.md", "PLANNING.md"):
        assert "org/intake" not in (REPO_ROOT / name).read_text(), f"{name} still references org/intake/"


def test_manifest_version_matches_readme():
    manifest = json.loads((REPO_ROOT / "FRAMEWORK-MANIFEST.json").read_text())
    assert manifest["version"] in (REPO_ROOT / "README.md").read_text()


def test_docs_reference_plural_routes_only():
    """bands.yaml schema uses 'routes'; docs must not show the singular form."""
    for name in ("PLANNING.md", "telemetry/bands.yaml"):
        content = (REPO_ROOT / name).read_text()
        assert not re.search(r"\broute:\s", content), f"{name} uses singular 'route:'"


def test_generated_project_state_is_not_shipped():
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "discovery/project.json"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    assert tracked.returncode != 0, "generated discovery state must not be tracked"
    ignored = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", "discovery/project.json"],
        cwd=REPO_ROOT,
        check=False,
    )
    assert ignored.returncode == 0, "generated discovery state must remain gitignored"
