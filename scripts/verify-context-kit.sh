#!/usr/bin/env bash
# Verifies context-kit structure and binds IDE rule files to canonical AGENTS.md.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

CHECK_ONLY=0
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=1

fail=0
note() { printf '  %s\n' "$*"; }
err() { printf '  FAIL: %s\n' "$*" >&2; fail=1; }

printf '\n[1/5] Required framework files\n'
for f in AGENTS.md SPEC.md PLANNING.md README.md project.config.yaml FRAMEWORK-MANIFEST.json scripts/test_guard.py; do
  if [[ -f "$f" ]]; then note "ok   $f"; else err "missing $f"; fi
done

printf '\n[2/5] Required directories\n'
for d in discovery docs/governance evals governance incidents scripts telemetry .claude/hooks .github/workflows; do
  if [[ -d "$d" ]]; then note "ok   $d/"; else err "missing $d/"; fi
done

printf '\n[3/5] Script syntax\n'
if command -v python3 >/dev/null 2>&1; then
  if python3 -m compileall -q scripts >/dev/null; then note 'ok   python scripts compile'; else err 'python scripts failed to compile'; fi
else
  err 'python3 not found (required, >=3.8)'
fi
for s in scripts/*.sh .claude/hooks/*.sh; do
  [[ -e "$s" ]] || continue
  if bash -n "$s"; then note "ok   $s"; else err "syntax error in $s"; fi
done

printf '\n[4/5] Executable bits\n'
for s in scripts/*.sh .claude/hooks/*.sh; do
  [[ -e "$s" ]] || continue
  if [[ -x "$s" ]]; then
    note "ok   $s"
  elif (( CHECK_ONLY )); then
    err "$s is not executable"
  else
    chmod +x "$s" && note "fixed $s (chmod +x)"
  fi
done

# Canonical rule source is AGENTS.md; every IDE rule file is a link to it.
printf '\n[5/5] IDE rule binding\n'
RULE_TARGETS=(.cursorrules .windsurfrules CLAUDE.md .github/copilot-instructions.md)

detect_ides() {
  local found=()
  [[ -d .cursor ]] && found+=("Cursor")
  [[ -d .windsurf ]] && found+=("Windsurf")
  [[ -d .claude ]] && found+=("Claude Code")
  [[ -d .github ]] && found+=("Copilot")
  [[ -d .codex || -f .codexrc ]] && found+=("Codex")
  printf '%s' "${found[*]:-none detected}"
}
note "environments: $(detect_ides)"

link_rule() {
  local target="$1" rel="$2"
  if [[ -L "$target" ]]; then
    if [[ "$(readlink "$target")" == "$rel" ]]; then note "ok   $target -> $rel"; else err "$target points to $(readlink "$target"), expected $rel"; fi
    return
  fi
  if [[ -f "$target" ]]; then
    err "$target exists as a regular file; move or delete it, then re-run (AGENTS.md is canonical)"
    return
  fi
  if (( CHECK_ONLY )); then err "$target is not linked to AGENTS.md"; return; fi
  mkdir -p "$(dirname "$target")"
  if ln -s "$rel" "$target" 2>/dev/null; then
    note "linked $target -> $rel"
  else
    cp AGENTS.md "$target" && note "copied AGENTS.md -> $target (symlinks unavailable)"
  fi
}

for target in "${RULE_TARGETS[@]}"; do
  if [[ "$target" == */* ]]; then link_rule "$target" "../AGENTS.md"; else link_rule "$target" "AGENTS.md"; fi
done

printf '\n'
if (( fail )); then
  printf 'Context kit verification: FAIL\n' >&2
  exit 1
fi
printf 'Context kit verification: PASS\n'
