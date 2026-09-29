import json

import org_status


def test_show_defaults_to_full_roster(workdir, capsys):
    assert org_status.main(["show"]) == 0
    out = capsys.readouterr().out
    for role in org_status.ROLES:
        assert role in out


def test_no_subcommand_shows_status(workdir, capsys):
    assert org_status.main([]) == 0
    assert "Software Factory Status" in capsys.readouterr().out


def test_set_persists_state(workdir):
    assert org_status.main(["set", "Worker", "busy", "--task", "plans/001-plan.md"]) == 0

    data = json.loads((workdir / "reviews/agent_org_status.json").read_text())
    assert data["roster"]["Worker"]["status"] == "busy"
    assert data["roster"]["Worker"]["active_task"] == "plans/001-plan.md"


def test_set_survives_reload(workdir, capsys):
    org_status.main(["set", "Planner", "blocked", "--task", "awaiting spec"])
    capsys.readouterr()
    org_status.main(["show", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["roster"]["Planner"]["status"] == "blocked"


def test_enqueue_and_dequeue(workdir):
    assert org_status.main(["enqueue", "PR-42", "--title", "Add checkout", "--assignee", "reviewer"]) == 0
    data = json.loads((workdir / "reviews/agent_org_status.json").read_text())
    assert data["review_queue"][0]["pr_id"] == "PR-42"

    assert org_status.main(["dequeue", "PR-42"]) == 0
    data = json.loads((workdir / "reviews/agent_org_status.json").read_text())
    assert data["review_queue"] == []


def test_duplicate_enqueue_rejected(workdir, capsys):
    org_status.main(["enqueue", "PR-42"])
    assert org_status.main(["enqueue", "PR-42"]) == 1
    assert "already queued" in capsys.readouterr().err


def test_dequeue_missing_pr_rejected(workdir, capsys):
    assert org_status.main(["dequeue", "PR-99"]) == 1
    assert "not in the queue" in capsys.readouterr().err


def test_reset_clears_state(workdir):
    org_status.main(["set", "Worker", "busy", "--task", "t"])
    org_status.main(["enqueue", "PR-1"])
    assert org_status.main(["reset"]) == 0

    data = json.loads((workdir / "reviews/agent_org_status.json").read_text())
    assert data["roster"]["Worker"]["status"] == "idle"
    assert data["review_queue"] == []


def test_corrupt_state_falls_back_to_defaults(workdir, capsys):
    (workdir / "reviews").mkdir()
    (workdir / "reviews/agent_org_status.json").write_text("{broken")
    assert org_status.main(["show", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["roster"]["CEO"]["type"] == "human"


def test_ceo_is_the_only_human(workdir, capsys):
    org_status.main(["show", "--json"])
    roster = json.loads(capsys.readouterr().out)["roster"]
    humans = [role for role, info in roster.items() if info["type"] == "human"]
    assert humans == ["CEO"]
    assert len(roster) == 10
