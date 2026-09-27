#!/usr/bin/env python3
# scripts/org_status.py — Agent Org State Machine & Review Queue Tracker
import json
import os
import sys

STATUS_FILE = "reviews/agent_org_status.json"

DEFAULT_ROSTER = {
    "CEO": {"type": "human", "status": "idle", "active_task": None},
    "CTO": {"type": "agent", "status": "idle", "active_task": None},
    "ProductManager": {"type": "agent", "status": "idle", "active_task": None},
    "Architect": {"type": "agent", "status": "idle", "active_task": None},
    "Planner": {"type": "agent", "status": "idle", "active_task": None},
    "Worker": {"type": "agent", "status": "idle", "active_task": None},
    "QA_Eval": {"type": "agent", "status": "idle", "active_task": None},
    "AdversarialReviewer": {"type": "agent", "status": "idle", "active_task": None},
    "ReleaseGate": {"type": "agent", "status": "idle", "active_task": None},
    "SRE_Ops": {"type": "agent", "status": "idle", "active_task": None}
}

def load_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"roster": DEFAULT_ROSTER, "review_queue": []}

def save_status(data):
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def print_status():
    data = load_status()
    print("\n--- 🤖 10-Agent Software Factory Status ---")
    for role, info in data["roster"].items():
        print(f"  • {role:<20} [{info['type']}] -> Status: {info['status']} | Task: {info['active_task'] or 'None'}")
    print(f"\n📥 Active Review Queue Items: {len(data['review_queue'])}")
    for q in data["review_queue"]:
        print(f"  - [{q.get('pr_id', 'N/A')}] {q.get('title', 'Untitled')} (Assigned: {q.get('assignee', 'Unassigned')})")
    print("-------------------------------------------\n")

if __name__ == "__main__":
    print_status()
