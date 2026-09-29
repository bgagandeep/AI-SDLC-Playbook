#!/usr/bin/env python3
"""Validate governance registers and telemetry bands against project.config.yaml."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

CONFIG_FILE = Path("project.config.yaml")
RISK_REGISTER = Path("governance/risk-register.yaml")
MODEL_INVENTORY = Path("governance/model-inventory.yaml")
SYSTEM_INVENTORY = Path("governance/system-inventory.yaml")
BANDS_FILE = Path("telemetry/bands.yaml")

RISK_CLASSES = ("Standard", "Elevated", "Critical")
BAND_ACTIONS = ("log", "diagnose", "propose")
REQUIRED_TIERS = ("1sigma", "2sigma", "3sigma")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing required file: {path}")
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def check_risk_register(errors: list[str], strict: bool) -> None:
    data = load_yaml(RISK_REGISTER)
    risks = data.get("risks") or []
    if not isinstance(risks, list):
        errors.append(f"{RISK_REGISTER}: 'risks' must be a list")
        return
    if strict and not risks:
        errors.append(f"{RISK_REGISTER}: risk_classification is 'required' but the register is empty")
    for index, risk in enumerate(risks, start=1):
        where = f"{RISK_REGISTER}[{index}]"
        if not isinstance(risk, dict):
            errors.append(f"{where}: entry must be a mapping")
            continue
        for field in ("id", "description", "risk_class", "owner", "mitigation"):
            if not risk.get(field):
                errors.append(f"{where}: missing required field '{field}'")
        risk_class = risk.get("risk_class")
        if risk_class and risk_class not in RISK_CLASSES:
            errors.append(f"{where}: risk_class {risk_class!r} not in {RISK_CLASSES}")


def check_inventory(errors: list[str], path: Path, key: str, fields: tuple[str, ...], strict: bool) -> None:
    data = load_yaml(path)
    items = data.get(key)
    if items is None:
        errors.append(f"{path}: missing top-level key '{key}'")
        return
    if not isinstance(items, list):
        errors.append(f"{path}: '{key}' must be a list")
        return
    if strict and not items and not data.get("not_applicable_reason"):
        errors.append(
            f"{path}: '{key}' is empty; add entries or a factual 'not_applicable_reason'"
        )
    for index, item in enumerate(items, start=1):
        where = f"{path}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: entry must be a mapping")
            continue
        for field in fields:
            if not item.get(field):
                errors.append(f"{where}: missing required field '{field}'")


def check_bands(errors: list[str]) -> None:
    data = load_yaml(BANDS_FILE)
    metrics = data.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        errors.append(f"{BANDS_FILE}: 'metrics' must be a non-empty list")
        return
    for index, metric in enumerate(metrics, start=1):
        where = f"{BANDS_FILE}[{index}]"
        if not isinstance(metric, dict):
            errors.append(f"{where}: entry must be a mapping")
            continue
        for field in ("name", "baseline", "rules"):
            if not metric.get(field):
                errors.append(f"{where}: missing required field '{field}'")
        tiers = metric.get("tiers")
        if not isinstance(tiers, dict):
            errors.append(f"{where}: 'tiers' must be a mapping")
            continue
        for tier in REQUIRED_TIERS:
            spec = tiers.get(tier)
            if not isinstance(spec, dict):
                errors.append(f"{where}.tiers.{tier}: missing or not a mapping")
                continue
            action = spec.get("action")
            if action not in BAND_ACTIONS:
                errors.append(f"{where}.tiers.{tier}: action {action!r} not in {BAND_ACTIONS}")
            if "route" in spec:
                errors.append(
                    f"{where}.tiers.{tier}: use plural 'routes' (list), not singular 'route'"
                )
            if action == "propose":
                routes = spec.get("routes")
                if not isinstance(routes, list) or not routes:
                    errors.append(f"{where}.tiers.{tier}: 'propose' requires a non-empty 'routes' list")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Permit empty registers even when project.config.yaml marks them required.",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    try:
        config = load_yaml(CONFIG_FILE)
        governance = config.get("governance") or {}
        strict_risk = governance.get("risk_classification") == "required" and not args.allow_empty
        strict_evidence = governance.get("evidence_binding") == "required" and not args.allow_empty

        check_risk_register(errors, strict_risk)
        check_inventory(errors, MODEL_INVENTORY, "models", ("id", "provider", "purpose", "owner"), strict_evidence)
        check_inventory(errors, SYSTEM_INVENTORY, "systems", ("id", "purpose", "owner", "risk_class"), strict_evidence)
        check_bands(errors)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        errors.append(str(exc))

    if errors:
        print("Governance validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Governance validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
