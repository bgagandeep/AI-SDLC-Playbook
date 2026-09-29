import shutil
from pathlib import Path

import pytest

import check_governance

REPO_ROOT = Path(__file__).resolve().parents[1]

VALID_BANDS = """
version: 1
metrics:
  - name: api_error_rate
    baseline: rolling_7d
    rules: western_electric
    tiers:
      1sigma: {action: log}
      2sigma: {action: diagnose}
      3sigma: {action: propose, routes: [intent_spec]}
"""


@pytest.fixture
def project(workdir):
    shutil.copy(REPO_ROOT / "project.config.yaml", workdir / "project.config.yaml")
    (workdir / "governance").mkdir()
    (workdir / "telemetry").mkdir()
    (workdir / "governance/risk-register.yaml").write_text("version: 1\nrisks: []\n")
    (workdir / "governance/model-inventory.yaml").write_text("version: 1\nmodels: []\n")
    (workdir / "governance/system-inventory.yaml").write_text("version: 1\nsystems: []\n")
    (workdir / "telemetry/bands.yaml").write_text(VALID_BANDS)
    return workdir


def test_empty_registers_fail_when_required(project, capsys):
    assert check_governance.main([]) == 1
    err = capsys.readouterr().err
    assert "register is empty" in err
    assert "'models' is empty" in err


def test_allow_empty_permits_stubs(project, capsys):
    assert check_governance.main(["--allow-empty"]) == 0
    assert "PASS" in capsys.readouterr().out


def test_explicit_not_applicable_model_inventory_is_valid(project, capsys):
    (project / "governance/model-inventory.yaml").write_text(
        "version: 1\n"
        "models: []\n"
        "not_applicable_reason: This project does not invoke models at runtime.\n"
    )
    (project / "governance/risk-register.yaml").write_text(
        "version: 1\nrisks:\n"
        "  - id: R-1\n    description: d\n    risk_class: Standard\n"
        "    owner: o\n    mitigation: m\n"
    )
    (project / "governance/system-inventory.yaml").write_text(
        "version: 1\nsystems:\n"
        "  - id: s1\n    purpose: p\n    owner: o\n    risk_class: Standard\n"
    )
    assert check_governance.main([]) == 0
    assert "PASS" in capsys.readouterr().out


def test_populated_registers_pass(project, capsys):
    (project / "governance/risk-register.yaml").write_text(
        "version: 1\n"
        "risks:\n"
        "  - id: R-001\n"
        "    description: Prompt injection via user content\n"
        "    risk_class: Critical\n"
        "    owner: appsec\n"
        "    mitigation: Untrusted-input isolation\n"
    )
    (project / "governance/model-inventory.yaml").write_text(
        "version: 1\nmodels:\n  - id: m1\n    provider: anthropic\n    purpose: codegen\n    owner: eng\n"
    )
    (project / "governance/system-inventory.yaml").write_text(
        "version: 1\nsystems:\n  - id: s1\n    purpose: triage\n    owner: eng\n    risk_class: Elevated\n"
    )
    assert check_governance.main([]) == 0
    assert "PASS" in capsys.readouterr().out


def test_invalid_risk_class_rejected(project, capsys):
    (project / "governance/risk-register.yaml").write_text(
        "version: 1\n"
        "risks:\n"
        "  - id: R-001\n"
        "    description: d\n"
        "    risk_class: catastrophic\n"
        "    owner: o\n"
        "    mitigation: m\n"
    )
    assert check_governance.main([]) == 1
    assert "not in ('Standard', 'Elevated', 'Critical')" in capsys.readouterr().err


def test_singular_route_key_rejected(project, capsys):
    (project / "telemetry/bands.yaml").write_text(
        VALID_BANDS.replace("routes: [intent_spec]", "route: intent_spec")
    )
    assert check_governance.main(["--allow-empty"]) == 1
    assert "use plural 'routes'" in capsys.readouterr().err


def test_propose_without_routes_rejected(project, capsys):
    (project / "telemetry/bands.yaml").write_text(
        VALID_BANDS.replace(", routes: [intent_spec]", "")
    )
    assert check_governance.main(["--allow-empty"]) == 1
    assert "requires a non-empty 'routes' list" in capsys.readouterr().err


def test_unknown_band_action_rejected(project, capsys):
    assert check_governance.main(["--allow-empty"]) == 0
    (project / "telemetry/bands.yaml").write_text(VALID_BANDS.replace("action: log", "action: escalate"))
    assert check_governance.main(["--allow-empty"]) == 1
    assert "action 'escalate' not in" in capsys.readouterr().err


def test_missing_tier_rejected(project, capsys):
    (project / "telemetry/bands.yaml").write_text(
        VALID_BANDS.replace("      3sigma: {action: propose, routes: [intent_spec]}\n", "")
    )
    assert check_governance.main(["--allow-empty"]) == 1
    assert "tiers.3sigma: missing" in capsys.readouterr().err


def test_missing_file_reported(project, capsys):
    (project / "governance/risk-register.yaml").unlink()
    assert check_governance.main(["--allow-empty"]) == 1
    assert "missing required file" in capsys.readouterr().err


def test_repo_bands_conform_to_schema():
    """The shipped telemetry/bands.yaml must satisfy the validator."""
    import os

    cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        assert check_governance.main([]) == 0
    finally:
        os.chdir(cwd)
