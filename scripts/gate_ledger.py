#!/usr/bin/env python3
"""SHA-256 hash-chained evidence ledger for quality and release gates.

Tamper-evidence is only meaningful when the chain head is anchored outside this
repository (signed tag, notary, or append-only store). Use `anchor` for that.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

LEDGER_FILE = Path("reviews/gate_ledger.json")
GENESIS_HASH = "0" * 64

# Risk classes are fixed by SPEC.md section 3.
RISK_CLASSES = ("Standard", "Elevated", "Critical")
APPROVER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._@+-]{1,63}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
GATE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{1,63}$")


class GateError(Exception):
    pass


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def entry_digest(entry: dict[str, Any]) -> str:
    """Hash every field except the digest itself, so no field can be altered silently."""
    payload = {k: v for k, v in entry.items() if k != "entry_hash"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_ledger() -> list[dict[str, Any]]:
    if not LEDGER_FILE.exists():
        return []
    try:
        data = json.loads(LEDGER_FILE.read_text())
    except json.JSONDecodeError as exc:
        raise GateError(f"{LEDGER_FILE} is corrupt: {exc}") from exc
    if not isinstance(data, list):
        raise GateError(f"{LEDGER_FILE} must contain a JSON array.")
    return data


def save_ledger(ledger: list[dict[str, Any]]) -> None:
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_FILE.write_text(json.dumps(ledger, indent=2) + "\n")


def commit_author(commit_sha: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%an <%ae>", commit_sha],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def validate(gate: str, commit: str, risk_class: str, approver: str) -> None:
    if not GATE_RE.match(gate):
        raise GateError(f"Invalid gate name {gate!r}.")
    if not COMMIT_RE.match(commit):
        raise GateError(f"Invalid commit SHA {commit!r}; expected 7-40 lowercase hex chars.")
    if risk_class not in RISK_CLASSES:
        raise GateError(f"Invalid risk class {risk_class!r}; expected one of {', '.join(RISK_CLASSES)}.")
    if not APPROVER_RE.match(approver):
        raise GateError(f"Invalid approver identity {approver!r}.")


def cmd_record(args: argparse.Namespace) -> int:
    validate(args.gate, args.commit, args.risk_class, args.approver)

    evidence_path = Path(args.evidence) if args.evidence else None
    if evidence_path is not None and not evidence_path.is_file():
        raise GateError(f"Evidence file not found: {evidence_path}")
    if args.risk_class in ("Elevated", "Critical") and evidence_path is None:
        raise GateError(f"{args.risk_class} gates require --evidence (SPEC.md section 3).")

    # AGENTS.md red line: an agent may not certify work it authored.
    author = commit_author(args.commit)
    if author and args.approver.lower() in author.lower() and not args.allow_self_certification:
        raise GateError(
            f"Self-certification blocked: approver {args.approver!r} authored {args.commit} ({author})."
        )

    ledger = load_ledger()
    verify_chain(ledger)

    entry: dict[str, Any] = {
        "index": len(ledger) + 1,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gate_name": args.gate,
        "commit_sha": args.commit,
        "risk_class": args.risk_class,
        "approver": args.approver,
        "evidence_file": str(evidence_path) if evidence_path else None,
        "evidence_hash": sha256_file(evidence_path) if evidence_path else None,
        "prev_hash": ledger[-1]["entry_hash"] if ledger else GENESIS_HASH,
    }
    entry["entry_hash"] = entry_digest(entry)

    ledger.append(entry)
    save_ledger(ledger)
    print(f"Ledger entry #{entry['index']} recorded for gate '{args.gate}'.")
    print(f"  entry_hash: {entry['entry_hash']}")
    return 0


def verify_chain(ledger: list[dict[str, Any]]) -> None:
    prev = GENESIS_HASH
    for position, entry in enumerate(ledger, start=1):
        if entry.get("index") != position:
            raise GateError(f"Entry at position {position} has index {entry.get('index')}.")
        if entry.get("prev_hash") != prev:
            raise GateError(f"Chain break at entry #{position}: prev_hash does not match entry #{position - 1}.")
        expected = entry_digest(entry)
        if entry.get("entry_hash") != expected:
            raise GateError(f"Entry #{position} has been tampered with (hash mismatch).")
        prev = entry["entry_hash"]


def cmd_verify(args: argparse.Namespace) -> int:
    ledger = load_ledger()
    verify_chain(ledger)

    stale: list[str] = []
    for entry in ledger:
        path = entry.get("evidence_file")
        if not path:
            continue
        evidence = Path(path)
        if not evidence.is_file():
            stale.append(f"entry #{entry['index']}: evidence missing ({path})")
        elif sha256_file(evidence) != entry.get("evidence_hash"):
            stale.append(f"entry #{entry['index']}: evidence modified since approval ({path})")

    if stale and not args.ignore_evidence:
        for line in stale:
            print(f"INVALID: {line}", file=sys.stderr)
        raise GateError("Evidence validity check failed.")

    head = ledger[-1]["entry_hash"] if ledger else GENESIS_HASH
    print(f"Ledger chain verified: {len(ledger)} entr{'y' if len(ledger) == 1 else 'ies'} intact.")
    print(f"  head: {head}")

    expected = os.environ.get("LEDGER_ANCHOR_HASH")
    if expected and expected != head:
        raise GateError(f"Head {head} does not match external anchor {expected}.")
    return 0


def cmd_anchor(_: argparse.Namespace) -> int:
    ledger = load_ledger()
    verify_chain(ledger)
    head = ledger[-1]["entry_hash"] if ledger else GENESIS_HASH
    print(head)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record", help="Append a gate approval to the ledger.")
    record.add_argument("--gate", required=True)
    record.add_argument("--commit", required=True)
    record.add_argument("--risk-class", required=True, choices=RISK_CLASSES)
    record.add_argument("--approver", required=True)
    record.add_argument("--evidence", default=None)
    record.add_argument(
        "--allow-self-certification",
        action="store_true",
        help="Override the no-self-certification red line (audited, use only with human sign-off).",
    )
    record.set_defaults(func=cmd_record)

    verify = sub.add_parser("verify", help="Verify chain integrity and evidence validity.")
    verify.add_argument("--ignore-evidence", action="store_true")
    verify.set_defaults(func=cmd_verify)

    anchor = sub.add_parser("anchor", help="Print the current chain head for external anchoring.")
    anchor.set_defaults(func=cmd_anchor)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except GateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
