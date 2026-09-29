# SPEC.md — Spec-Driven Agentic Development (SDAD) Framework

## 1. Philosophy & Architecture
Spec-Driven Agentic Development (SDAD) establishes **"version control for human thinking"**. As context windows expand to millions of tokens, specification precision becomes the primary execution fuel for autonomous delivery. Code is generated downstream from immutable, machine-actionable specifications.

---

## 2. Core Spec-Driven Artifact Templates

### 2.1 Intent Specification Template (`intent.md`)
*Location: `intent/INTENT_NAME.md`*

```markdown
# Intent: [Short Feature or Incident Title]
Author: [Name/Agent] | Status: [draft | accepted | rejected] | Date: [YYYY-MM-DD]

## Problem Statement
[Clear description of the pain point, user impact, or operational failure]

## Proposed Outcome
[Measurable end state of what success looks like]

## Affected Users & Systems
[Impacted user personas, microservices, APIs, or database schemas]

## Technical & Business Constraints
[Security boundaries, zero-PII rules, latency budgets, platform dependencies]

## Open Questions
[Unresolved technical or business ambiguities requiring human input]
```

---

### 2.2 Functional & Architectural Spec Template (`spec.md`)
*Location: `specs/SPEC_NAME.md`*

```markdown
# Spec: [Feature Name] (Derived from intent/INTENT_NAME.md)
Status: [ready-for-plan | under-review | approved]

## 1. Functional & Non-Functional Requirements
1. [Requirement 1: System SHALL...]
2. [Requirement 2: Latency MUST remain below...]

## 2. System Architecture & Interface Contracts
- [API Endpoints, Data Models, Schema Definitions]
- [Architectural Decision Records (ADRs) and Product Decisions (PDs) Applied]

## 3. Encoded Skills & Policies Applied
- Security Policy: `.claude/skills/secure-api-review/SKILL.md`
- Data Classification: PII/PHI Sanitization Policy v2
- UI/UX: Design System Component Standards

## 4. ISO/IEC 42001 AI Governance & Risk Controls
- [ ] **Prompt Injection Defense**: Input validation schema and untrusted text isolation rules defined.
- [ ] **Model Context Boundary**: System prompt and memory retrieval boundaries isolated from user-generated content.
- [ ] **Data Privacy & PII Boundary**: Zero PII/PHI logged in LLM prompt payloads or telemetry traces.
- [ ] **Hallucination & Fallback Guard**: Deterministic fallback paths defined for non-deterministic model outputs.

## 5. Flagged Policy Concerns
[Explicitly flag conflicting policies or trade-offs requiring Policy Owner sign-off]
```

---

### 2.3 Implementation Plan Template (`plan.md`)
*Location: `plans/PLAN_NAME.md`*

```markdown
# Plan: [Task Name] (Derived from specs/SPEC_NAME.md)
Risk Class: [Standard | Elevated | Critical]

## Target File Manifest
- Modify: `src/services/payment.py`
- Create: `src/components/CheckoutPanel.tsx`
- Test: `tests/unit/test_payment.py`, `tests/integration/test_checkout.py`

## Ordered Execution DAG
1. Step 1: Create failing integration test for payment route (`pytest tests/integration/test_checkout.py`).
2. Step 2: Implement payment handler logic in `src/services/payment.py`.
3. Step 3: Wire frontend CheckoutPanel component to backend endpoint.

## Risk Profile & Mitigation
- Identified Risk: Rate-limiting on core payment gateway.
- Mitigation: Implement Redis sliding-window caching layer.

## Verifiable Proof of Completion
- `pytest tests/` and `npm run test` pass 100%.
- Playwright screenshot diff matches approved Figma mockup.
```

---

## 3. Risk Profile Classification & Evidence Requirements
Every proposed change is assigned a Risk Class that dictates its required evidence package and gate permissions:

| Risk Class | Change Criteria | Verification Required | Gate Permission |
| :--- | :--- | :--- | :--- |
| **Standard** | Localized, non-breaking, easily reversible (e.g., UI tweaks, docs). | Automated unit tests (`npm run test` / `pytest`), linter clean. | Single Engineer approval after green CI. |
| **Elevated** | API contract changes, schema updates, dependency bumps, data pipelines. | Risk-derived property tests, contract tests, independent agent review, canary deployment. | Tech Lead / Code Owner sign-off required. |
| **Critical** | Authentication, payment logic, PII/PHI handling, ISO 42001 AI boundary, migrations. | Multi-agent adversarial review, threat model validation, rollback dry-run, and provenance evidence when the project produces deployable artifacts. | Separation of Duties: Dual Human Sign-off (Domain Owner + AppSec). |

---

## 4. Decision Contract & Trustworthy Evidence
A Quality Gate evaluates evidence against policy to authorize state transitions. Evidence must fulfill five trustworthiness criteria:
1. **Independent Origin**: Produced by a verification mechanism independent of the authoring agent.
2. **Exact Revision Binding**: Hard-linked to the specific Git commit SHA and, when configured by the adopting project, build provenance.
3. **Producer Integrity**: Generated inside an isolated, trusted CI runner.
4. **Current Validity**: Free from invalidating events (subsequent commits invalidate prior test runs).
5. **Risk Coverage**: Directly maps to a harm or requirement flagged in the Risk Profile.

---

## 5. Machine-Verifiable Definition of Done (DoD)
A feature branch cannot merge until the following evidence package is validated:
- [ ] `plan.md` committed and verified against eventual diff.
- [ ] 100% passing tests (`pytest` / `npm run test` / `flutter test`).
- [ ] Zero static analysis warnings (`flake8` / `eslint` / `flutter analyze`).
- [ ] ISO/IEC 42001 AI Governance Pass passed with zero high-severity findings.
- [ ] Visual UI verification screenshot captured and verified via Playwright.
- [ ] Multi-pass code review completed (`REVIEW.md`) with 0 'Important' findings.
- [ ] Continuous eval suite pass rate > 95% on regression benchmark.
- [ ] Hash-chained approval ledger entry recorded via `scripts/gate_ledger.py` and chain head anchored externally for tamper resistance.

## 6. Discovery & Baseline Contract
Every repository takeover starts with a read-only discovery pass. Capture technology, architecture, dependencies, data flows, deployment, security, test/quality baseline, observability, and technical debt. Preserve pre-existing failures separately from change-induced failures.

## 7. Change Impact Assessment
Each plan records affected components, interfaces, data, users, security implications, operational implications, rollback strategy, and risk class.

## 8. Evidence States
Evidence is classified as `verified`, `inferred`, `assumed`, or `unknown`. Gate decisions cannot treat inferred or assumed facts as verified evidence.
