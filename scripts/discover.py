#!/usr/bin/env python3
"""Create a lightweight project discovery report without modifying source code."""
from pathlib import Path
import json

ROOT = Path.cwd()
checks = {
    "git": (ROOT / ".git").exists(),
    "python": any((ROOT / f).exists() for f in ["pyproject.toml", "requirements.txt", "setup.py"]),
    "node": any((ROOT / f).exists() for f in ["package.json", "pnpm-workspace.yaml"]),
    "flutter": (ROOT / "pubspec.yaml").exists(),
    "go": (ROOT / "go.mod").exists(),
    "rust": (ROOT / "Cargo.toml").exists(),
    "java_maven": (ROOT / "pom.xml").exists(),
    "java_gradle": any((ROOT / f).exists() for f in ["build.gradle", "build.gradle.kts"]),
    "dotnet": any(ROOT.glob("*.sln")) or any(ROOT.glob("*.csproj")),
    "docker": (ROOT / "Dockerfile").exists(),
}
report = {
    "status": "baseline-discovery",
    "facts": {k: {"value": v, "confidence": "verified"} for k, v in checks.items()},
    "unknowns": [],
}
Path("discovery/project.json").write_text(json.dumps(report, indent=2) + "\n")
print("Discovery report written to discovery/project.json")
