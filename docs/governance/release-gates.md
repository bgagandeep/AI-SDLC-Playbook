# Release Gates

A production release should have, as applicable:

1. Functional tests passing.
2. Static analysis passing.
3. Security/dependency checks reviewed.
4. AI evaluation results recorded for material AI behavior.
5. Risk register reviewed for changed risks.
6. Change Impact Assessment completed for material changes.
7. Required governance approvals/evidence linked.
8. Incident rollback/response path known.
9. Model, prompt, data, and external-service changes traceable.
10. Deployment and monitoring evidence available.

A gate may be marked **Not Applicable** only when the project records the rationale.
Do not convert failed checks into successful checks with `|| true`, unconditional fallback success, or equivalent suppression.
