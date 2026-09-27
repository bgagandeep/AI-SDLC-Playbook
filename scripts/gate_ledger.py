#!/usr/bin/env python3
# scripts/gate_ledger.py — SHA-256 Cryptographic Evidence Ledger Generator
import os
import sys
import json
import hashlib
import time

LEDGER_FILE = "reviews/gate_ledger.json"

def compute_file_sha256(filepath):
    if not os.path.exists(filepath):
        return "file_not_found"
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def record_approval(gate_name, commit_sha, risk_class, approver, evidence_file):
    ledger = []
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, "r") as f:
                ledger = json.load(f)
        except Exception:
            ledger = []

    prev_hash = ledger[-1]["entry_hash"] if ledger else "0" * 64
    evidence_hash = compute_file_sha256(evidence_file) if evidence_file else "N/A"

    entry = {
        "index": len(ledger) + 1,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gate_name": gate_name,
        "commit_sha": commit_sha,
        "risk_class": risk_class,
        "approver": approver,
        "evidence_file": evidence_file,
        "evidence_hash": evidence_hash,
        "prev_hash": prev_hash
    }

    entry_data = f"{entry['index']}{entry['timestamp']}{gate_name}{commit_sha}{risk_class}{approver}{evidence_hash}{prev_hash}"
    entry["entry_hash"] = hashlib.sha256(entry_data.encode("utf-8")).hexdigest()

    ledger.append(entry)

    os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

    print(f"✅ Cryptographic Ledger Entry #{entry['index']} recorded for gate '{gate_name}'. Hash: {entry['entry_hash'][:16]}...")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 gate_ledger.py <gate_name> <commit_sha> <risk_class> <approver> [evidence_file]")
        sys.exit(1)
    
    g_name = sys.argv[1]
    c_sha = sys.argv[2]
    r_class = sys.argv[3]
    appr = sys.argv[4]
    ev_file = sys.argv[5] if len(sys.argv) > 5 else None

    record_approval(g_name, c_sha, r_class, appr, ev_file)
