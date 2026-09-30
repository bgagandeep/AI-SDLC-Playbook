# AI-Native SDLC Framework — Podcast Annexure & Execution Kit

> **Official Companion Kit for the Podcast Episode: *Orchestrating the AI-Native Software Factory***
> *Based on research & playbooks from Anthropic, Cursor, Microsoft, Gas City, and Spec-Driven Agentic Development (SDAD).*

Welcome to the **AI-Native SDLC Framework**. When code generation speeds up by 10x–100x through frontier agents (Claude Code, Cursor, Codex), traditional human-speed approval gates and manual PR reviews become the primary bottleneck—creating a "verification tax." 

This kit transforms policy declarations into **machine-verifiable, executable controls**. It establishes an autonomous 10-agent software factory with a 7-phase closed-loop lifecycle, allowing teams to move from zero to their first governed feature in ~10 minutes, or safely take over existing legacy codebases.

---

## 🚀 Quick Start (0 → First Governed Feature in 10 Minutes)

**Requirements:** Python ≥ 3.9, Bash, `openssl`, and `git`. Optional: Bun (for the Cursor grind hook).

### Step 1: Clone or Copy this Framework into Your Workspace
Clone this repository from its source host (or copy the kit into an existing project), then install the validation toolchain:
```bash
cd my-project
pip install -r requirements.txt
```

### Step 2: Run the Environment Verification & Rule Linker
Do NOT manually copy or blindly symlink rules. Run the verification script — it checks required files and directories, byte-compiles the Python scripts, syntax-checks the shell hooks, repairs executable bits, detects your IDE environment (Cursor, Windsurf, Claude Code, Copilot, Codex), and symlinks each IDE rule file to canonical `AGENTS.md`:
```bash
bash scripts/verify-context-kit.sh
```
Use `--check` for a read-only audit that fails instead of repairing (this is what CI runs).

### Step 3: Establish Your Phase 0 Baseline
```bash
python3 scripts/discover.py            # scans the current repo
python3 scripts/discover.py --root ../legacy-app   # or any brownfield target
```
This writes `discovery/project.json` with `verified` facts and an explicit `unknowns` list that a human or agent must resolve before planning.

### Step 4: Capture Your First Intent (`intent.md`)
Create a new intent in `intent/001-initial-feature.md` or ask your Product Manager Agent:
```markdown
# Intent: Add Customer Self-Service Dashboard
Author: Lead Architect | Status: draft | Date: 2026-09-26

## Problem Statement
Users flood support with status requests because order tracking is invisible.

## Proposed Outcome
A real-time order tracking panel in the web app backed by PostgreSQL.
```

### Step 5: Trigger the Agentic Pipeline
Launch your coding agent (Cursor Plan Mode `Shift+Tab` or `claude --permission-mode plan`):
```text
@AGENTS.md Read intent/001-initial-feature.md, generate specs/001-spec.md following SPEC.md, and create plans/001-plan.md.
```

### Step 6: Execute via Isolated TDD Worktree
Once `001-plan.md` is approved, launch a Worker Agent in an isolated Git worktree:
```bash
claude --worktree feature/order-tracking
```
The Worker Agent will:
1. Write failing tests (`pytest` / `npm run test` / `flutter test`).
2. Confirm the red state, then lock tests with `python3 scripts/test_guard.py lock <test-path>`.
3. Write green implementation code until all tests pass.
4. Unlock tests with `python3 scripts/test_guard.py unlock --all` and run applicable Playwright visual verification.
5. Open a Pull Request with hash-chained evidence attached (`scripts/gate_ledger.py`).

### Step 7: Record and Verify Gate Evidence
```bash
python3 scripts/gate_ledger.py record \
  --gate quality-gate --commit "$(git rev-parse HEAD)" \
  --risk-class Elevated --approver reviewer-id --evidence reviews/REVIEW.md
python3 scripts/gate_ledger.py verify
```
The ledger refuses risk classes outside `Standard|Elevated|Critical`, requires evidence for Elevated and Critical gates, and blocks an approver who authored the commit under review.

---

## ✅ Verifying This Framework

```bash
bash scripts/verify-context-kit.sh --check   # structure, syntax, permissions, rule links
python3 scripts/check_governance.py           # register + telemetry band schemas
pytest tests/ -v                              # full test suite
```

---

## 🏗️ Framework Architecture

```
                                  +------------------------------------+
                                  |     CEO / Human Lead (You)         |
                                  +-----------------+------------------+
                                                    | (Intent & Gate Approvals)
                                                    v
                                  +------------------------------------+
                                  |     CTO / Lead Orchestrator        |
                                  +-----------------+------------------+
                                                    |
     +-------------------+------------+-------------+------------+-------------------+
     |                   |            |                          |                   |
     v                   v            v                          v                   v
+----+----+      +-------+----+  +----+---+              +-------+-------+   +-------+-------+
| Product |      | Architect  |  | Planner|              | QA & Eval     |   | SRE & Ops     |
| Manager |      | & Design   |  | Agent  |              | Agent         |   | Agent (Closed)|
+----+----+      +-------+----+  +----+---+              +-------+-------+   +-------+-------+
     |                   |            |                          |                   |
     +-------------------+------+-----+--------------------------+                   |
                                |                                                    |
                                v                                                    |
                        +-------+-------+                                            |
                        | Worker / Dev  |                                            |
                        | Implementation|                                            |
                        +-------+-------+                                            |
                                |                                                    |
                                v                                                    |
                        +-------+-------+                                            |
                        | Adversarial   |                                            |
                        | Reviewer Agent|                                            |
                        +-------+-------+                                            |
                                |                                                    |
                                v                                                    |
                        +-------+-------+                                            |
                        | Release Gate  |<-------------------------------------------+
                        | Agent         |     (3σ Telemetry Breach Feedback Loop)
                        +---------------+
```

---

## 📁 Repository Structure & Directory Map

```text
ai-native-sdlc/
├── README.md                      # This 10-minute Quick Start & Podcast Annexure Guide
├── AGENTS.md                      # Canonical Orchestration Engine (10-agent roster & MCP rules)
├── SPEC.md                        # Spec-Driven Development Framework & ISO 42001 Checklist
├── PLANNING.md                    # 7-Phase LifeCycle, TDD Loop & 3σ Telemetry Control Bands
├── FRAMEWORK-MANIFEST.json        # Framework version and declared principles
├── project.config.yaml            # Project-level governance and auto-detection settings
├── requirements.txt               # Python toolchain (Python >= 3.9)
├── intent/                        # Phase 1 Artifacts (proto-specs)
├── specs/                         # Phase 2 Artifacts (functional & architectural specs)
├── plans/                         # Phase 3 Artifacts (execution DAGs & file manifests)
├── reviews/                       # Phase 5 Artifacts (review findings, ledger & org state, gitignored)
├── discovery/                     # Phase 0 baseline discovery reports
├── governance/                    # ISO/IEC 42001 registers (risk, model, system inventories)
├── evals/                         # Continuous evaluation benchmark suites
├── incidents/                     # Incident records feeding back into Phase 1
├── docs/
│   └── governance/
│       └── release-gates.md       # Release gate criteria and Not-Applicable rules
├── .claude/
│   ├── hooks/
│   │   └── production-gate.sh     # Executable bash hook blocking unauthorized deploys
│   └── settings.json              # Production gate, test guard & secret-path deny rules
├── .cursor/
│   ├── hooks/
│   │   └── grind.ts               # Bun/TS hook for autonomous TDD iteration loops
│   └── hooks.json                 # Cursor stop hook & shell interception registration
├── scripts/
│   ├── verify-context-kit.sh      # Environment detection & IDE rule linking script
│   ├── gate_ledger.py             # SHA-256 hash-chained evidence ledger (record/verify/anchor)
│   ├── org_status.py              # Agent state machine and review queue tracker
│   ├── discover.py                # Phase 0 read-only project discovery
│   ├── check_governance.py        # Governance register & telemetry band schema validator
│   └── test_guard.py              # Red-test lock CLI and PreToolUse enforcement hook
├── tests/                         # pytest suite covering every script and the hook
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Framework integrity + per-stack lint/test enforcement
│       ├── security.yml           # Governance validation, secret scan, dep audit, CodeQL
│       └── release-gate.yml       # Separation-of-duties release authorization workflow
└── telemetry/
    └── bands.yaml                 # Western Electric 3σ telemetry control bands configuration
```

> `intent/`, `specs/`, and `plans/` ship with template READMEs and receive project artifacts on first use.
> `discovery/project.json` and `reviews/` state (`gate_ledger.json`, `agent_org_status.json`)
> are generated per project and gitignored by default.
> IDE rule files (`.cursorrules`, `.windsurfrules`, `CLAUDE.md`,
> `.github/copilot-instructions.md`) are symlinks to `AGENTS.md` created by
> `scripts/verify-context-kit.sh` — never edit them directly.

---

## 🎯 Greenfield vs. Brownfield Execution Modes

### Greenfield Kickoff (0 → 1)
1. Drop this repository structure into a new folder.
2. Run `bash scripts/verify-context-kit.sh`.
3. Fill out `intent/001-feature.md` and instruct your Planner Agent to generate `specs/` and `plans/`.
4. Let the Worker Agent execute in TDD mode until all tests pass green.

### Brownfield / Legacy Project Takeover
1. Copy `AGENTS.md`, `SPEC.md`, `PLANNING.md`, `.claude/`, `.cursor/`, `.github/`, `scripts/`, `governance/`, and `telemetry/` into your existing project root.
2. Run `bash scripts/verify-context-kit.sh`.
3. Run `python3 scripts/discover.py` to capture the Phase 0 baseline, then record pre-existing test/lint/security failures so agents do not inherit blame for them.
4. Launch your Planner Agent in **Plan Mode** (`Shift+Tab` or `--permission-mode plan`).
5. Instruct the agent: *"Map the existing codebase, document unwritten architecture rules in AGENTS.md, and create a refactoring plan in plans/001-legacy-migration.md."*
6. Execute changes in isolated Git worktrees (`git worktree add`) without touching the working branch directly.

## v1.2.0 Governance & Brownfield Additions

This release combines the reusable onboarding and developer-experience scaffolding from the original framework with the governance, discovery, evidence, evaluation, risk, and brownfield capabilities introduced in v1.1.0.

### v1.2.0 principles
- Works for greenfield and brownfield/takeover projects.
- Treats AI systems as governed socio-technical systems, not only software components.
- Keeps evidence, risk, evaluation, change impact, and incident artifacts close to the project.
- Fails quality gates explicitly rather than converting failures into successful builds.
- Keeps framework scaffolding lightweight enough to adopt incrementally.

---

## ⚠️ Scope & Limitations

- **Hash chain ≠ proof.** `gate_ledger.py` is tamper-**evident**, not tamper-**proof**. Anyone with write access can recompute the whole chain. Anchor the head externally (`gate_ledger.py anchor` → signed tag or append-only store) and set `LEDGER_ANCHOR_HASH` in CI for a real integrity guarantee.
- **The production gate depends on secret hygiene.** Anyone holding `RELEASE_APPROVAL_SECRET` can mint tokens. Store it as a protected CI secret only.
- **Release tokens are job-scoped.** The release workflow masks the token and writes it only to `GITHUB_ENV`; add the adopter's deployment step to that same protected job after `Verify production authorization`.
- **MCP servers are not bundled.** The optional registry in `AGENTS.md` lists integrations you must configure and authorize yourself.
- **Branch protection is external.** Configure protected `main`/`master` rules and a protected `production` environment with required reviewers and self-review prevention in the Git host.
- **Artifact provenance is adopter-owned.** This framework validates source controls; projects producing deployable artifacts must add their own build and provenance workflow.
- **ISO/IEC 42001 alignment is scaffolding, not certification.** Certification requires organization-specific assessment and evidence.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).
