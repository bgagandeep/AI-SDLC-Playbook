#!/usr/bin/env bash
# Blocks deploy/production commands until a signed human release token is present.
# Invoked as a PreToolUse hook; receives the candidate command on argv or stdin.
set -euo pipefail

BLOCK_EXIT=2

if [[ $# -gt 0 ]]; then
  COMMAND="$*"
else
  INPUT="$(cat || true)"
  COMMAND="$(
    python3 -c 'import json,sys
raw=sys.stdin.read()
try:
    event=json.loads(raw)
    print(event.get("tool_input", {}).get("command", ""))
except (json.JSONDecodeError, AttributeError):
    print(raw)' <<< "$INPUT"
  )"
fi

# Only intercept commands that actually target a release path.
if ! printf '%s' "$COMMAND" | grep -Eqi '(^|[^a-z])(deploy|production|prod-release|release:prod)([^a-z]|$)'; then
  exit 0
fi

if [[ -z "${RELEASE_APPROVAL:-}" ]]; then
  echo "BLOCKED: production gate. RELEASE_APPROVAL token is not set." >&2
  echo "A human release manager must authorize this command." >&2
  exit "$BLOCK_EXIT"
fi

# Token format: <approver>:<commit_sha>:<hmac>
if ! printf '%s' "$RELEASE_APPROVAL" | grep -Eq '^[A-Za-z0-9._@-]+:[0-9a-f]{7,40}:[0-9a-f]{64}$'; then
  echo "BLOCKED: production gate. RELEASE_APPROVAL is malformed." >&2
  echo "Expected <approver>:<commit_sha>:<hmac-sha256>." >&2
  exit "$BLOCK_EXIT"
fi

if [[ -z "${RELEASE_APPROVAL_SECRET:-}" ]]; then
  echo "BLOCKED: production gate. RELEASE_APPROVAL_SECRET is not configured." >&2
  exit "$BLOCK_EXIT"
fi

APPROVER="${RELEASE_APPROVAL%%:*}"
REST="${RELEASE_APPROVAL#*:}"
COMMIT_SHA="${REST%%:*}"
SUPPLIED_HMAC="${REST#*:}"

EXPECTED_HMAC="$(
  printf '%s:%s' "$APPROVER" "$COMMIT_SHA" |
    openssl dgst -sha256 -hmac "$RELEASE_APPROVAL_SECRET" -r |
    cut -d' ' -f1
)"

if [[ "$SUPPLIED_HMAC" != "$EXPECTED_HMAC" ]]; then
  echo "BLOCKED: production gate. RELEASE_APPROVAL signature is invalid." >&2
  exit "$BLOCK_EXIT"
fi

# Bind the token to HEAD only when HEAD actually resolves (a repo with no commits must not crash the gate).
if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
  if HEAD_SHA="$(git rev-parse --verify HEAD 2>/dev/null)"; then
    if [[ "$HEAD_SHA" != "$COMMIT_SHA"* ]]; then
      echo "BLOCKED: production gate. Token is bound to $COMMIT_SHA but HEAD is $HEAD_SHA." >&2
      exit "$BLOCK_EXIT"
    fi
  fi
fi

echo "Production gate: authorized by $APPROVER for $COMMIT_SHA."
exit 0
