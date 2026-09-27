# PLANNING.md — Agentic SDLC Workflow & Execution Guide

## 1. End-to-End Agentic SDLC Lifecycle Graph
The software lifecycle operates as a continuous directed graph loop across 7 discrete phases:

```
[Phase 1: Intent] ──► [Phase 2: Design] ──► [Phase 3: Plan] ──► [Phase 4: Build/TDD]
       ▲                                                                 │
       │                                                                 ▼
[Phase 7: SRE/Ops] ◄── [Phase 6: Deploy] ◄─────────────────────── [Phase 5: Test/Eval]
  (3σ Telemetry Breach)   (Release Gate)                           (Multi-Pass Review)
```

---

### Phase 1: Intent Capture (`intent.md`)
- **Action**: Human lead or Product Manager Agent captures raw demand, incident alerts, or user requests.
- **Process**: Brainstorm with the agent to convert unstructured input into `intent/INTENT_NAME.md`.
- **Gate**: Human product owner accepts and merges `intent.md`.

### Phase 2: Requirements & Design Synthesis (`spec.md`)
- **Action**: Architect Agent ingests accepted `intent.md`, loads project skills (`.claude/skills/`), and generates `specs/SPEC_NAME.md`.
- **Process**: Agent flags policy conflicts, security boundary risks, or ISO/IEC 42001 governance concerns.
- **Gate**: Product Owner and Technical Lead sign off on `spec.md`.

### Phase 3: Recursive Planning & Task Decomposition (`plan.md`)
- **Action**: Engineer launches Planner Agent in Plan Mode (`Shift+Tab` or `--permission-mode plan`).
- **Process**: Planner Agent explores codebase using instant `grep` and semantic search. Maps files changing, execution order, and risk profile into `plans/PLAN_NAME.md`.
- **Gate**: Engineer approves `plan.md`. Plan mode locks workspace edits until accepted.

### Phase 4: Isolated Build & TDD Execution
- **Action**: Orchestrator spawns Worker Agent in an isolated Git worktree (`claude --worktree` or `.cursor/worktrees`).
- **Process (TDD Protocol)**:
  1. Agent writes failing test cases based on `plan.md` proof criteria (`pytest` / `npm run test` / `flutter test`).
  2. Agent executes tests to confirm red failure state.
  3. Red test file is locked via hook (`PreToolUse` block on test edit).
  4. Agent writes implementation code until all tests pass green.
  5. Agent runs local feedback loop and Playwright browser verification.

### Phase 5: Continuous Evals & Multi-Pass PR Review
- **Action**: Worker Agent opens Pull Request.
- **Process**:
  1. CI pipeline executes Continuous Evals suite (20–50 benchmark tasks).
  2. Adversarial Reviewer Agent runs `REVIEW.md` 4-Pass Review:
     - **Pass 1: Logic & Regression Pass**: Subtle logic bugs, race conditions, edge-case regressions.
     - **Pass 2: Security & Vulnerability Pass**: Injection risks, authentication gaps, secret leaks.
     - **Pass 3: Spec & Architecture Compliance Pass**: Verifies diff strictly matches `spec.md` and `plan.md`.
     - **Pass 4: ISO/IEC 42001 AI Governance Pass**: Evaluates AI-specific components for LLM prompt injection vulnerabilities, system prompt context leaks, unhandled model hallucination states, and zero-PII prompt logging compliance.
  3. Worker Agent automatically addresses comments tagged `@claude` and pushes fixes.
- **Gate**: Code Owner approves PR based on review findings and eval pass rate.

### Phase 6: Sandboxed Deployment & Gate Enforcement
- **Action**: CI/CD pipeline triggers deployment workflow.
- **Process**: Code is deployed to isolated staging sandboxes (Azure Container Apps Dynamic Sessions or Railway environments).
- **Gate**: Production Gate hook (`.claude/hooks/production-gate.sh`) intercepts release command. Deploy halts until signed human release manager authorization token (`RELEASE_APPROVAL`) is present.

### Phase 7: SRE/Ops & Closed-Loop Autonomous Operations
- **Action**: SRE Agent continuously watches live telemetry using Western Electric control bands (`bands.yaml`).
- **Process**: Evaluates 3σ statistical deviations on production metrics.

#### Production `bands.yaml` Control Configuration:
```yaml
# Telemetry Control Bands for Active Deployments (e.g., WhatsApp AI Assistant - Disha)
metrics:
  - name: whatsapp_api_webhook_timeout_rate
    baseline: rolling_7d
    rules: western_electric
    tiers:
      1sigma: { action: log }
      2sigma: { action: diagnose, tools: "Read,Grep,mcp/railway" }
      3sigma: { action: propose, routes: [intent_spec, runbook:scale-worker] }

  - name: cloudflare_ai_gateway_token_cost_spike
    baseline: rolling_24h
    rules: western_electric
    tiers:
      1sigma: { action: log }
      2sigma: { action: diagnose, tools: "Read,mcp/cloudflare" }
      3sigma: { action: propose, routes: [intent_spec, runbook:fallback-model] }

  - name: postgresql_connection_pool_exhaustion
    baseline: rolling_7d
    rules: western_electric
    tiers:
      1sigma: { action: log }
      2sigma: { action: diagnose, tools: "Read,mcp/postgresql" }
      3sigma: { action: propose, routes: [intent_spec, runbook:restart-pool] }
```

- **Closed-Loop Action**: When a 3σ breach occurs (e.g., WhatsApp API timeout spike >3σ), the SRE Agent automatically writes a diagnostic `intent/INTENT_NAME.md` file, triggering Phase 1 to restart the SDLC loop autonomously.

---

## 2. Long-Running Agent Loop Config (`grind.ts`)
To allow Worker Agents to run autonomously without getting stuck, configure local loop hooks in `.cursor/hooks.json` or `.claude/settings.json`:

```json
{
  "version": 1,
  "hooks": {
    "stop": [
      {
        "command": "bun run .cursor/hooks/grind.ts"
      }
    ]
  }
}
```

---

## 3. Context Pruning & Conversation Reset Protocol
To eliminate context degradation and "verification tax" overhead, agents must follow strict conversation management rules:

- **When to Start a Fresh Conversation**:
  1. Moving to a new phase or discrete task in `plan.md`.
  2. Agent repeats the same mistake twice or appears confused.
  3. Total conversation turn count exceeds 15 exchanges.
- **Resetting vs. Debugging**: If an agent produces a broken implementation, do NOT spend turns arguing with it. Revert git changes back to `plan.md`, refine the prompt/plan, and launch a fresh session.
- **Referencing Prior Work**: Use `@Chats` or pass specific SHA references rather than copy-pasting full past conversation transcripts.

## Phase 0: Discovery & Baseline
Run `python3 scripts/discover.py` and expand the generated discovery record as needed. Establish the pre-change state before implementation. For brownfield work, baseline existing tests, lint, type, security, build, and deployment failures.

## Universal Stop Conditions
Pause for human input when requirements conflict, production state is unknown, destructive changes are proposed, rollback is unavailable for critical changes, secrets are exposed, critical security findings appear, or governance/policy ownership is unclear.

## Incident Loop
Detection → Triage → Containment → Recovery → Root Cause Analysis → Corrective Action → new Intent.
