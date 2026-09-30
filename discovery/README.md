# Discovery & Baseline

Phase 0 for every project. Establish the repository, stack, architecture, dependencies, deployment, security, tests, and known technical debt before changing code.

Record facts as `verified`, `inferred`, `assumed`, or `unknown`. Capture the pre-change test/lint/security baseline so agents do not claim ownership of pre-existing failures.

Run `python3 scripts/discover.py` to generate `discovery/project.json`. The report is project-specific runtime state and is intentionally gitignored by this starter; adopting projects may force-add an approved baseline when they need it as versioned evidence.
