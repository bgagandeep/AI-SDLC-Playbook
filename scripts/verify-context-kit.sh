#!/usr/bin/env bash
set -euo pipefail
for f in AGENTS.md SPEC.md PLANNING.md README.md project.config.yaml; do test -f "$f" || { echo "Missing $f"; exit 1; }; done
python3 -m py_compile scripts/*.py
bash -n .claude/hooks/production-gate.sh
printf 'Context kit structure and scripts: PASS\n'
