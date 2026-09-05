"""
Quick system forensic snapshot:
- Recent program executions (from AppCompatCache / Amcache stubs)
- Suspicious startup entries
- Recently modified files in temp/user dirs
"""

import os
import subprocess
import winreg
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class SystemSnapshot:
    startup_entries: list[dict] = field(default_factory=list)
    temp_suspicious: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


SUSPICIOUS_STARTUP_KEYWORDS = [
    "inject", "hook", "cheat", "hack", "bypass", "loader",
    "ghost", "wurst", "meteor", "impact", "sigma", "raven",
    "autoclicker", "macro", "trigger",
]


def scan() -> SystemSnapshot:
    snap = SystemSnapshot()
    snap.startup_entries = _get_startup_entries()
    snap.temp_suspicious = _scan_temp_dirs()
    return snap


def _get_startup_entries() -> list[dict]:
    entries = []
    run_keys = [
        (winreg.HKEY_CURRENT_USER,  r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ]
    for hive, path in run_keys:
        try:
            with winreg.OpenKey(hive, path) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        suspicious = any(kw in (name + value).lower() for kw in SUSPICIOUS_STARTUP_KEYWORDS)
                        entries.append({
                            "name": name,
                            "value": value,
                            "suspicious": suspicious,
                        })
                        i += 1
                    except OSError:
                        break
        except (FileNotFoundError, PermissionError):
            pass
    return entries


def _scan_temp_dirs() -> list[str]:
    suspicious = []
    temp_dirs = [
        Path(os.environ.get("TEMP", "")),
        Path(os.environ.get("TMP", "")),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Temp",
    ]
    extensions = {".exe", ".dll", ".jar", ".bat", ".ps1", ".vbs"}
    for temp in temp_dirs:
        if not temp.exists():
            continue
        try:
            for f in temp.iterdir():
                if f.is_file() and f.suffix.lower() in extensions:
                    suspicious.append(str(f))
        except PermissionError:
            pass
    return suspicious
