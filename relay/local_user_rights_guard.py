#!/usr/bin/env python3
"""CF-098: read-only source guard for current-user, limited-rights HP scheduling.

This inspects checked-in scripts only. A passing result does not attest the
principal of a task already installed on a real Windows computer.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
INSTALL = ROOT / "relay" / "install_task.ps1"
WRITEBACK = ROOT / "relay" / "cf_public_relay_rw.ps1"
HEALTH = ROOT / "relay" / "configure_health_reporting.ps1"


def uncomment(source: str) -> str:
    # Full-line PowerShell comments aren't executable authority.
    return "\n".join(line for line in source.splitlines()
                     if not line.lstrip().startswith("#"))


def audit(install: str, writeback: str, health: str) -> list[str]:
    errors: list[str] = []
    installer = uncomment(install)
    rw = uncomment(writeback)
    report = uncomment(health)
    flat = re.sub(r"\s+", " ", installer)

    if not re.search(r"\$user\s*=\s*\[Security\.Principal\.WindowsIdentity\]::GetCurrent\(\)\.Name", flat, re.I):
        errors.append("installer must use the current Windows identity")
    principals = re.findall(r"\bNew-ScheduledTaskPrincipal\b[^\r\n]*", installer, re.I)
    if len(principals) != 1:
        errors.append("installer must define exactly one scheduled-task principal")
    else:
        p = principals[0]
        for flag in (r"-UserId\s+\$user\b", r"-LogonType\s+Interactive\b", r"-RunLevel\s+Limited\b"):
            if not re.search(flag, p, re.I):
                errors.append("scheduled principal missing " + flag)
    if not re.search(r"\bRegister-ScheduledTask\b[^\r\n]*-Principal\s+\$principal\b", installer, re.I):
        errors.append("registered task must use the checked principal")

    # Enable/disable writeback may update the existing *action*; it must not
    # replace the task principal, privilege set or user context.
    for label, source in (("installer", installer), ("writeback", rw), ("health", report)):
        if not re.search(r"['\"]CavemanFocusCF0Relay['\"]", source):
            errors.append(label + " must reference the existing CF-0 task")
        for expression in (
            r"(?i)-RunLevel\s+Highest\b",
            r"(?i)-UserId\s+['\"]?(?:SYSTEM|NT\s+AUTHORITY\\SYSTEM|Administrators)\b",
            r"(?i)Start-Process\b[^\r\n]*-Verb\s+RunAs\b",
            r"(?i)\bschtasks(?:\.exe)?\b[^\r\n]*/ru\s+(?:SYSTEM|Administrator)",
            r"(?i)\bInvoke-Expression\b",
        ):
            if re.search(expression, source):
                errors.append(label + " attempts elevated or dynamic command execution")
    for label, source in (("writeback", rw), ("health", report)):
        if re.search(r"(?i)\b(?:New-ScheduledTaskPrincipal|Register-ScheduledTask)\b", source):
            errors.append(label + " must not create or replace the principal")
        if re.search(r"(?i)\bSet-ScheduledTask\b[^\r\n]*-Principal\b", source):
            errors.append(label + " must not modify user principal")
    if not re.search(r"\bSet-ScheduledTask\s+-TaskName\s+\$TaskName\s+-Action\s+\$action\b", rw, re.I):
        errors.append("writeback must alter only the existing task action")
    if re.search(r"(?i)\b(?:Set-ScheduledTask|Unregister-ScheduledTask)\b", report):
        errors.append("health opt-in must not modify or remove the schedule")
    return errors


def main() -> int:
    problems = audit(INSTALL.read_text(encoding="utf-8"),
                     WRITEBACK.read_text(encoding="utf-8"),
                     HEALTH.read_text(encoding="utf-8"))
    for error in problems:
        print("CF-098 FAIL:", error)
    if problems:
        return 1
    print("CF-098 source guard PASSED: current-user limited principal; no elevated writeback or health override")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
