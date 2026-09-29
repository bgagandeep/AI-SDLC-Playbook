import json

import pytest

import gate_ledger


def record(**overrides):
    args = {
        "gate": "quality-gate",
        "commit": "abc1234",
        "risk_class": "Standard",
        "approver": "reviewer",
        "evidence": None,
        "allow_self_certification": False,
    }
    args.update(overrides)
    return gate_ledger.main(
        [
            "record",
            "--gate",
            args["gate"],
            "--commit",
            args["commit"],
            "--risk-class",
            args["risk_class"],
            "--approver",
            args["approver"],
            *(["--evidence", str(args["evidence"])] if args["evidence"] else []),
            *(["--allow-self-certification"] if args["allow_self_certification"] else []),
        ]
    )


def test_record_creates_chained_entries(workdir):
    assert record() == 0
    assert record(gate="release-gate") == 0

    ledger = json.loads((workdir / "reviews/gate_ledger.json").read_text())
    assert [e["index"] for e in ledger] == [1, 2]
    assert ledger[0]["prev_hash"] == gate_ledger.GENESIS_HASH
    assert ledger[1]["prev_hash"] == ledger[0]["entry_hash"]


def test_verify_passes_on_intact_chain(workdir, capsys):
    record()
    assert gate_ledger.main(["verify"]) == 0
    assert "verified" in capsys.readouterr().out


def test_verify_detects_field_tampering(workdir, capsys):
    record(risk_class="Standard")
    path = workdir / "reviews/gate_ledger.json"
    ledger = json.loads(path.read_text())
    ledger[0]["risk_class"] = "Critical"
    path.write_text(json.dumps(ledger))

    assert gate_ledger.main(["verify"]) == 1
    assert "tampered" in capsys.readouterr().err


def test_verify_detects_chain_break(workdir, capsys):
    record()
    record(gate="second-gate")
    path = workdir / "reviews/gate_ledger.json"
    ledger = json.loads(path.read_text())
    del ledger[0]
    ledger[0]["index"] = 1
    ledger[0]["entry_hash"] = gate_ledger.entry_digest(ledger[0])
    path.write_text(json.dumps(ledger))

    assert gate_ledger.main(["verify"]) == 1
    assert "Chain break" in capsys.readouterr().err


@pytest.mark.parametrize("risk_class", ["low", "HIGH", "standard", ""])
def test_invalid_risk_class_rejected(workdir, risk_class):
    with pytest.raises(SystemExit) as exc:
        record(risk_class=risk_class)
    assert exc.value.code == 2  # argparse choices rejection


def test_invalid_commit_sha_rejected(workdir, capsys):
    assert record(commit="not-a-sha") == 1
    assert "Invalid commit SHA" in capsys.readouterr().err


def test_invalid_approver_rejected(workdir, capsys):
    assert record(approver="a b; rm -rf /") == 1
    assert "Invalid approver" in capsys.readouterr().err


def test_elevated_gate_requires_evidence(workdir, capsys):
    assert record(risk_class="Elevated") == 1
    assert "require --evidence" in capsys.readouterr().err


def test_critical_gate_accepts_evidence(workdir):
    evidence = workdir / "evidence.txt"
    evidence.write_text("test results")
    assert record(risk_class="Critical", evidence=evidence) == 0

    ledger = json.loads((workdir / "reviews/gate_ledger.json").read_text())
    assert ledger[0]["evidence_hash"] == gate_ledger.sha256_file(evidence)


def test_missing_evidence_file_rejected(workdir, capsys):
    assert record(risk_class="Critical", evidence=workdir / "nope.txt") == 1
    assert "Evidence file not found" in capsys.readouterr().err


def test_verify_detects_modified_evidence(workdir, capsys):
    evidence = workdir / "evidence.txt"
    evidence.write_text("original")
    record(risk_class="Critical", evidence=evidence)
    evidence.write_text("swapped after approval")

    assert gate_ledger.main(["verify"]) == 1
    assert "evidence modified" in capsys.readouterr().err


def test_self_certification_blocked(workdir, capsys, monkeypatch):
    monkeypatch.setattr(gate_ledger, "commit_author", lambda sha: "Reviewer <reviewer@example.com>")
    assert record(approver="reviewer") == 1
    assert "Self-certification blocked" in capsys.readouterr().err


def test_self_certification_override_is_explicit(workdir, monkeypatch):
    monkeypatch.setattr(gate_ledger, "commit_author", lambda sha: "Reviewer <reviewer@example.com>")
    assert record(approver="reviewer", allow_self_certification=True) == 0


def test_anchor_prints_head(workdir, capsys):
    record()
    capsys.readouterr()
    assert gate_ledger.main(["anchor"]) == 0
    head = capsys.readouterr().out.strip()
    ledger = json.loads((workdir / "reviews/gate_ledger.json").read_text())
    assert head == ledger[-1]["entry_hash"]


def test_anchor_mismatch_fails_verify(workdir, capsys, monkeypatch):
    record()
    monkeypatch.setenv("LEDGER_ANCHOR_HASH", "f" * 64)
    assert gate_ledger.main(["verify"]) == 1
    assert "does not match external anchor" in capsys.readouterr().err


def test_corrupt_ledger_reported(workdir, capsys):
    (workdir / "reviews").mkdir()
    (workdir / "reviews/gate_ledger.json").write_text("{not json")
    assert gate_ledger.main(["verify"]) == 1
    assert "corrupt" in capsys.readouterr().err
