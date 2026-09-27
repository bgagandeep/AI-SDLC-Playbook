# AI-Native SDLC Framework — Podcast Annexure & Execution Kit

> **Official Companion Kit for the Podcast Episode: *Orchestrating the AI-Native Software Factory***
> *Based on research & playbooks from Anthropic, Cursor, Microsoft, Gas City, and Spec-Driven Agentic Development (SDAD).*

Welcome to the **AI-Native SDLC Framework**. When code generation speeds up by 10x–100x through frontier agents (Claude Code, Cursor, Codex), traditional human-speed approval gates and manual PR reviews become the primary bottleneck—creating a "verification tax." 

This kit transforms policy declarations into **machine-verifiable, executable controls**. It establishes an autonomous 10-agent software factory with a 7-phase closed-loop lifecycle, allowing teams to move from zero to their first governed feature in ~10 minutes, or safely take over existing legacy codebases.

---

## 🚀 Quick Start (0 → First Governed Feature in 10 Minutes)

### Step 1: Clone or Copy this Framework into Your Workspace
```bash
git clone https://github.com/your-org/ai-native-sdlc.git my-project
cd my-project
```

### Step 2: Run the Environment Verification & Rule Linker
Do NOT manually copy or blindly symlink rules. Run the smart verification script to detect your IDE environment (Cursor, Windsurf, Claude Code, Codex), verify symlink capability, and bind rule configurations to canonical `AGENTS.md`:
```bash
chmod +x scripts/verify-context-kit.sh
./scripts/verify-context-kit.sh
```

### Step 3: Capture Your First Intent (`intent.md`)
Create a new intent in `intent/001-initial-feature.md` or ask your Product Manager Agent:
```markdown
# Intent: Add Customer Self-Service Dashboard
Author: Lead Architect | Status: draft | Date: 2026-09-26

## Problem Statement
Users flood support with status requests because order tracking is invisible.

## Proposed Outcome
A real-time order tracking panel in the web app backed by PostgreSQL.
```

### Step 4: Trigger the Agentic Pipeline
Launch your coding agent (Cursor Plan Mode `Shift+Tab` or `claude --permission-mode plan`):
```text
@AGENTS.md Read intent/001-initial-feature.md, generate specs/001-spec.md following SPEC.md, and create plans/001-plan.md.
```

### Step 5: Execute via Isolated TDD Worktree
Once `001-plan.md` is approved, launch a Worker Agent in an isolated Git worktree:
```bash
claude --worktree feature/order-tracking
```
The Worker Agent will:
1. Write failing tests (`pytest` / `npm run test` / `flutter test`).
2. Lock test files via PreToolUse hooks.
3. Write green implementation code until all tests pass.
4. Run Playwright visual verification.
5. Open a Pull Request with cryptographic evidence attached (`scripts/gate_ledger.py`).

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
├── intent/                        # Phase 1 Artifacts (proto-specs)
├── specs/                         # Phase 2 Artifacts (functional & architectural specs)
├── plans/                         # Phase 3 Artifacts (execution DAGs & file manifests)
├── reviews/                       # Phase 5 Artifacts (4-pass code review findings)
├── .claude/
│   ├── hooks/
│   │   └── production-gate.sh    # Executable bash hook blocking unauthorized deploys
│   └── settings.json              # PreToolUse hook configuration & managed sandbox settings
├── .cursor/
│   ├── hooks/
│   │   └── grind.ts              # Bun/TS hook for autonomous TDD iteration loops
│   └── hooks.json                 # Cursor stop hook registration
├── scripts/
│   ├── verify-context-kit.sh     # Environment detection & smart IDE rule linking script
│   ├── gate_ledger.py            # SHA-256 cryptographic evidence ledger generator
│   └── org_status.py             # Agent state machine and review queue tracker
├── .github/
│   └── workflows/
│       ├── ci.yml                # Automated CI: 100% test pass + lint enforcement
│       ├── security.yml          # ISO/IEC 42001 AI governance & SLSA provenance check
│       └── release-gate.yml      # Signed release token authorization workflow
└── telemetry/
    └── bands.yaml                # Western Electric 3σ telemetry control bands configuration
```

---

## 🎯 Greenfield vs. Brownfield Execution Modes

### Greenfield Kickoff (0 → 1)
1. Drop this repository structure into a new folder.
2. Run `./scripts/verify-context-kit.sh`.
3. Fill out `intent/001-feature.md` and instruct your Planner Agent to generate `specs/` and `plans/`.
4. Let the Worker Agent execute in TDD mode until all tests pass green.

### Brownfield / Legacy Project Takeover
1. Copy `AGENTS.md`, `SPEC.md`, `PLANNING.md`, `.claude/`, `.cursor/`, and `scripts/` into your existing project root.
2. Run `./scripts/verify-context-kit.sh`.
3. Launch your Planner Agent in **Plan Mode** (`Shift+Tab` or `--permission-mode plan`).
4. Instruct the agent: *"Map the existing codebase, document unwritten architecture rules in CLAUDE.md, and create a refactoring plan in plans/001-legacy-migration.md."*
5. Execute changes in isolated Git worktrees (`git worktree add`) without touching the working branch directly.

## v1.2.0 Governance & Brownfield Additions

This release combines the reusable onboarding and developer-experience scaffolding from the original framework with the governance, discovery, evidence, evaluation, risk, and brownfield capabilities introduced in v1.1.0.

### v1.2.0 principles
- Works for greenfield and brownfield/takeover projects.
- Treats AI systems as governed socio-technical systems, not only software components.
- Keeps evidence, risk, evaluation, change impact, and incident artifacts close to the project.
- Fails quality gates explicitly rather than converting failures into successful builds.
- Keeps framework scaffolding lightweight enough to adopt incrementally.
