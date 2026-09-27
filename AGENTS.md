# AGENTS.md — Unified AI-Native SDLC Orchestration Engine

## 1. Multi-IDE Unification & Rule Synchronization
To prevent agent behavioral drift across IDEs (Cursor, Windsurf, Claude Code, Codex), `AGENTS.md` serves as the single source of truth for repository memory and operational rules.

### One-Touch Symlink & Verification Setup
Run the environment verification script to bind rules to this canonical file:
```bash
./scripts/verify-context-kit.sh
```
*Rule: Do NOT edit `.cursorrules`, `.windsurfrules`, or `CLAUDE.md` directly. Update `AGENTS.md` and commit changes to version control.*

---

## 2. Multi-Agent Roster & Organizational Hierarchy
Derived from the Gas City 10-Agent Software Factory and Anthropic's Agent Org architecture:

```
                ┌──────────────────────────────────────────┐
                │          CEO / Human Lead (You)          │
                └────────────────────┬─────────────────────┘
                                     │ (Intent & Release Authorization)
                                     ▼
                ┌──────────────────────────────────────────┐
                │           CTO / Lead Orchestrator        │
                └────────────────────┬─────────────────────┘
                                     │
     ┌──────────────────┬────────────┼─────────────┬──────────────────┐
     ▼                  ▼            ▼             ▼                  ▼
┌─────────┐      ┌────────────┐┌──────────┐ ┌──────────────┐ ┌──────────────────┐
│ Product │      │ Architect  ││ Planner  │ │ QA & Eval    │ │ SRE & Ops Agent  │
│ Manager │      │ & Design   ││ Agent    │ │ Agent        │ │ (Closed-Loop)    │
└────┬────┘      └─────┬──────┘└────┬─────┘ └──────┬───────┘ └────────┬─────────┘
     │                 │            │              │                  │
     └─────────────────┴──────┬─────┴──────────────┘                  │
                              ▼                                       │
                      ┌───────────────┐                               │
                      │ Worker / Dev  │                               │
                      │ Implementation│                               │
                      └───────┬───────┘                               │
                              ▼                                       │
                      ┌───────────────┐                               │
                      │ Adversarial   │                               │
                      │ Reviewer Agent│                               │
                      └───────┬───────┘                               │
                              ▼                                       │
                      ┌───────────────┐                               │
                      │ Release Gate  │◄──────────────────────────────┘
                      │ Agent         │  (3σ Telemetry Breach Loop)
                      └───────────────┘
```

### Role & Authority Contracts:
1. **CEO / Human Lead**: Retains sole authority over intent approval, spec/plan disagreement resolution, PR merge authorization, and production release gating.
2. **CTO / Lead Orchestrator**: Manages global task routing, monitors agent busy/idle states via `scripts/org_status.py`, enforces workspace context boundaries, and coordinates parallel worktrees.
3. **Product Manager Agent**: Transforms human and system demand in `org/intake/` into version-controlled `intent.md` proto-specs.
4. **Architect & Design Agent**: Synthesizes `intent.md` into `spec.md`. Enforces system architecture rules, Architectural Decision Records (ADRs), and Product Decisions (PDs).
5. **Planner Agent (Recursive)**: Operates strictly in Plan Mode (`--permission-mode plan` or `Shift+Tab`). Explores codebases, maps dependency DAGs, and generates `plan.md` without editing source files.
6. **Worker / Implementation Agent**: Executes single tasks in isolated Git worktrees (`.cursor/worktrees` or `claude --worktree`). Operates in auto-accept mode once `plan.md` is approved.
7. **QA & Eval Agent**: Drives Test-Driven Development (TDD) red-to-green loops, property-based testing, and executes continuous evaluation suites (20–50 benchmark tasks) in CI.
8. **Adversarial Reviewer Agent**: Conducts multi-pass PR reviews (`REVIEW.md`: Bugs, Security, Compliance, ISO/IEC 42001 AI Governance). Cannot certify its own code.
9. **Release & Deployment Agent**: Manages dynamic sandboxed execution environments, verifies SLSA provenance, and enforces the `production-gate.sh` hook.
10. **SRE & Operations Agent (Closed-Loop)**: Continuous telemetry watcher (`bands.yaml`). Evaluates 3σ control band breaches and writes diagnostic `intent.md` files back to re-enter the SDLC.

---

## 3. Tech Stack & Testing Paradigm Execution Rules
Agents must run exact test and lint commands corresponding to the target module:

| Module / Tech Stack | Unit & Integration Testing Command | Linter / Static Analysis Command |
| :--- | :--- | :--- |
| **Python Backend Services** | `pytest tests/unit/ tests/integration/ -v --cov=src` | `flake8 src/ && mypy src/` |
| **Next.js / TypeScript Frontend** | `npm run test` (or `vitest run` / `jest --passWithNoTests`) | `npm run lint` (`eslint . --ext .ts,.tsx`) |
| **Flutter / Dart Mobile App** | `flutter test --coverage` | `flutter analyze` |
| **End-to-End Visual Verification**| `npx playwright test` (captures Playwright diffs) | `npx playwright codegen` |

*TDD Rule*: During bug-fix tasks, agents write failing test cases first. PreToolUse hooks block modifications to test files during the implementation pass.

---

## 4. Active Model Context Protocol (MCP) Server Registry
Agents interact with databases, infrastructure, and tools strictly via active MCP integrations:

- **PostgreSQL MCP (`mcp/postgresql`)**: Schema inspection, query optimization, migration dry-runs, latency analysis.
- **Railway MCP (`mcp/railway`)**: Container service deployment status, environment variables, build logs.
- **Firebase MCP (`mcp/firebase`)**: Firestore rule verification, FCM push notification debugging, Auth claims inspection.
- **Cloudflare MCP (`mcp/cloudflare`)**: AI Gateway token metrics, Worker route deployment, Workers AI logs.
- **GitHub MCP (`mcp/github`)**: Pull request management, issue syncing, CI/CD run inspections.
- **Playwright MCP (`mcp/playwright`)**: Browser automation, visual UI screenshot diffs, end-to-end user flow execution.

---

## 5. Behavioral Red Lines & Security Guardrails
- **No Self-Certification**: An agent that writes code or tests is strictly forbidden from approving its own PR or certifying its evidence.
- **Locked Test Files During Fixes**: Hooks block edits to test files while implementing a fix to prove bug resolution.
- **No Direct Master/Main Pushes**: All code changes must originate in an isolated worktree branch and arrive via a Pull Request.
- **Credential & Secret Isolation**: Deny read access to `~/.aws/credentials`, `~/.ssh`, `.env*`, and root secret paths.
- **Production Gate Intercept**: Any command containing `deploy` or `production` invokes `.claude/hooks/production-gate.sh` and halts until explicit, signed human release authorization is provided.

## 11. Universal Project Discovery
Before planning any change, run Phase 0 discovery. Record stack, architecture, dependencies, deployment, security boundaries, tests, observability, and baseline failures. Classify findings as verified, inferred, assumed, or unknown. Never invent missing architecture.

## 12. Agent Stop Conditions
Agents must stop and request human resolution for conflicting requirements, destructive or irreversible changes, unknown production state, unavailable rollback for critical changes, discovered secrets, critical security findings, ambiguous authorization semantics, or policy conflicts.

## 13. Authority Boundary
Agents may propose and implement within their assigned scope but may not approve their own work, merge protected branches, or authorize production release.
