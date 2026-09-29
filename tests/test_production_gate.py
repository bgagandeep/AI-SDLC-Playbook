"""Behavioural tests for the production release gate hook."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / ".claude/hooks/production-gate.sh"
SECRET = "test-secret"


def run_hook(command: str, env_extra: dict[str, str] | None = None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("RELEASE_APPROVAL")}
    env.update(env_extra or {})
    return subprocess.run(
        ["bash", str(HOOK), command],
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
        check=False,
    )


def run_json_hook(
    command: str,
    env_extra: dict[str, str] | None = None,
    event_extra: dict[str, str] | None = None,
):
    env = {k: v for k, v in os.environ.items() if not k.startswith("RELEASE_APPROVAL")}
    env.update(env_extra or {})
    return subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps(
            {
                "tool_name": "Bash",
                "tool_input": {"command": command},
                **(event_extra or {}),
            }
        ),
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
        check=False,
    )


def hmac(approver: str, commit: str, secret: str = SECRET) -> str:
    result = subprocess.run(
        ["openssl", "dgst", "-sha256", "-hmac", secret, "-r"],
        input=f"{approver}:{commit}",
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.split()[0]


@pytest.mark.parametrize("command", ["npm run build", "pytest tests/", "git status", "ls -la"])
def test_non_release_commands_pass_through(command):
    assert run_hook(command).returncode == 0


@pytest.mark.parametrize(
    "command",
    ["kubectl deploy app", "make production", "npm run release:prod", "./deploy.sh"],
)
def test_release_commands_blocked_without_token(command):
    result = run_hook(command)
    assert result.returncode == 2
    assert "RELEASE_APPROVAL token is not set" in result.stderr


def test_malformed_token_blocked():
    result = run_hook("make deploy", {"RELEASE_APPROVAL": "just-a-string"})
    assert result.returncode == 2
    assert "malformed" in result.stderr


def test_missing_secret_blocked():
    commit = "a" * 40
    token = f"alice:{commit}:{'0' * 64}"
    result = run_hook("make deploy", {"RELEASE_APPROVAL": token})
    assert result.returncode == 2
    assert "RELEASE_APPROVAL_SECRET is not configured" in result.stderr


def test_forged_signature_blocked():
    commit = "a" * 40
    token = f"alice:{commit}:{'0' * 64}"
    result = run_hook(
        "make deploy",
        {"RELEASE_APPROVAL": token, "RELEASE_APPROVAL_SECRET": SECRET},
    )
    assert result.returncode == 2
    assert "signature is invalid" in result.stderr


def test_signature_from_wrong_secret_blocked():
    commit = "a" * 40
    token = f"alice:{commit}:{hmac('alice', commit, 'attacker-secret')}"
    result = run_hook(
        "make deploy",
        {"RELEASE_APPROVAL": token, "RELEASE_APPROVAL_SECRET": SECRET},
    )
    assert result.returncode == 2
    assert "signature is invalid" in result.stderr


def test_valid_token_authorizes():
    commit = "a" * 40
    token = f"alice:{commit}:{hmac('alice', commit)}"
    result = run_hook(
        "make deploy",
        {"RELEASE_APPROVAL": token, "RELEASE_APPROVAL_SECRET": SECRET},
    )
    # Passes signature check; a real git repo may additionally reject the SHA binding.
    assert result.returncode == 0 or "bound to" in result.stderr


def test_token_bound_to_wrong_commit_is_rejected_in_git_repo():
    if subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], capture_output=True).returncode != 0:
        pytest.skip("not a git repository with commits")
    commit = "b" * 40
    token = f"alice:{commit}:{hmac('alice', commit)}"
    result = run_hook(
        "make deploy",
        {"RELEASE_APPROVAL": token, "RELEASE_APPROVAL_SECRET": SECRET},
    )
    assert result.returncode == 2
    assert "bound to" in result.stderr


def test_substring_match_does_not_trigger():
    """'deployment' inside a word should not falsely trip the gate matcher."""
    assert run_hook("cat docs/deployment-notes.md").returncode == 0


def test_claude_json_event_is_parsed():
    result = run_json_hook("make deploy")
    assert result.returncode == 2
    assert "RELEASE_APPROVAL token is not set" in result.stderr


def test_non_command_json_fields_do_not_trigger_gate():
    result = run_json_hook("echo hello", event_extra={"description": "deploy to production"})
    assert result.returncode == 0
