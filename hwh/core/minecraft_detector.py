"""
Detects Minecraft installations, launcher accounts, and suspicious client artifacts.
Works offline — reads local registry, AppData, and known paths.
"""

import os
import json
import winreg
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# ── Known cheat client fingerprints ──────────────────────────────────────────
CHEAT_CLIENT_SIGNATURES = {
    # Folder names inside AppData / roaming / local
    "folders": [
        ".wurst", "wurst",
        ".meteor", "meteor-client",
        ".impact", "impact",
        ".baritone",
        "liquidbounce", ".liquidbounce",
        "vanta", ".vanta",
        "sigma",
        "aristois",
        "inertia",
        "future",
        "rusherhack",
        "raven",
        "novoline",
        ".novoline",
        "salhack",
        ".freelook",
        "autoclicker",
        "ghost-client",
        ".ghost",
        "labymod-addons",         # some addons are suspicious
    ],
    # Executable / JAR names
    "files": [
        "wurst*.jar", "meteor*.jar", "impact*.jar",
        "liquidbounce*.jar", "vanta*.jar", "sigma*.jar",
        "aristois*.jar", "inertia*.jar", "future*.jar",
        "rusherhack*.jar", "raven*.jar", "novoline*.jar",
        "freelook*.jar", "ghost*.jar",
        "autoclicker.exe", "ghost.exe",
    ],
}

MINECRAFT_LAUNCHER_PATHS = [
    Path(os.environ.get("APPDATA", "")) / ".minecraft",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Packages" / "Microsoft.4297127D64EC6_8wekyb3d8bbwe" / "LocalCache" / "Local" / "runtime",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Minecraft" / "launcher",
]

# Launcher profile JSON locations
LAUNCHER_PROFILES = [
    Path(os.environ.get("APPDATA", "")) / ".minecraft" / "launcher_profiles.json",
    Path(os.environ.get("APPDATA", "")) / ".minecraft" / "launcher_accounts.json",
]

SEARCH_ROOTS = [
    Path(os.environ.get("APPDATA", "")),
    Path(os.environ.get("LOCALAPPDATA", "")),
    Path(os.environ.get("APPDATA", "")) / ".minecraft",
]


@dataclass
class MinecraftAccount:
    username: str
    uuid: Optional[str] = None
    account_type: str = "Unknown"   # Mojang / Microsoft / Local
    last_used: Optional[str] = None
    source: str = ""


@dataclass
class CheatArtifact:
    name: str
    path: str
    kind: str   # "folder" | "file"
    severity: str = "High"


@dataclass
class MinecraftScanResult:
    accounts: list[MinecraftAccount] = field(default_factory=list)
    installations: list[str] = field(default_factory=list)
    cheat_artifacts: list[CheatArtifact] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def scan() -> MinecraftScanResult:
    result = MinecraftScanResult()
    result.accounts = _find_accounts()
    result.installations = _find_installations()
    result.cheat_artifacts = _find_cheat_artifacts()
    return result


# ── Account detection ─────────────────────────────────────────────────────────

def _find_accounts() -> list[MinecraftAccount]:
    accounts: list[MinecraftAccount] = []

    for profile_path in LAUNCHER_PROFILES:
        if not profile_path.exists():
            continue
        try:
            data = json.loads(profile_path.read_text(encoding="utf-8"))
            _parse_launcher_json(data, accounts, str(profile_path))
        except Exception as e:
            pass  # silently skip malformed files

    # Deduplicate by UUID
    seen = set()
    unique = []
    for acc in accounts:
        key = acc.uuid or acc.username
        if key not in seen:
            seen.add(key)
            unique.append(acc)

    return unique


def _parse_launcher_json(data: dict, accounts: list, source: str):
    # launcher_accounts.json format (newer launcher)
    if "accounts" in data:
        for uid, acc in data["accounts"].items():
            username = (
                acc.get("minecraftProfile", {}).get("name")
                or acc.get("username")
                or acc.get("displayName")
                or "Unknown"
            )
            uuid = acc.get("minecraftProfile", {}).get("id") or uid
            acc_type = acc.get("type", "Unknown").capitalize()
            accounts.append(MinecraftAccount(
                username=username,
                uuid=uuid,
                account_type=acc_type,
                source=source,
            ))

    # launcher_profiles.json format (older launcher)
    elif "authenticationDatabase" in data:
        for uid, acc in data["authenticationDatabase"].items():
            username = (
                acc.get("displayName")
                or acc.get("username")
                or "Unknown"
            )
            accounts.append(MinecraftAccount(
                username=username,
                uuid=uid,
                account_type="Mojang",
                source=source,
            ))


# ── Installation detection ────────────────────────────────────────────────────

def _find_installations() -> list[str]:
    found = []
    for path in MINECRAFT_LAUNCHER_PATHS:
        if path.exists():
            found.append(str(path))

    # Check registry for Minecraft Launcher install
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                            0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, sub) as sub_key:
                        try:
                            name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                            if "minecraft" in name.lower():
                                try:
                                    loc, _ = winreg.QueryValueEx(sub_key, "InstallLocation")
                                    if loc and loc not in found:
                                        found.append(f"[Registry] {name}: {loc}")
                                except FileNotFoundError:
                                    pass
                        except FileNotFoundError:
                            pass
                    i += 1
                except OSError:
                    break
    except Exception:
        pass

    return found


# ── Cheat artifact detection ──────────────────────────────────────────────────

def _find_cheat_artifacts() -> list[CheatArtifact]:
    artifacts: list[CheatArtifact] = []

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        # Check suspicious folder names (only 1 level deep for speed)
        try:
            for item in root.iterdir():
                if item.is_dir():
                    name_lower = item.name.lower()
                    for sig in CHEAT_CLIENT_SIGNATURES["folders"]:
                        if sig == name_lower:
                            artifacts.append(CheatArtifact(
                                name=item.name,
                                path=str(item),
                                kind="folder",
                                severity="High",
                            ))
                            break
        except PermissionError:
            pass

    # Deeper scan inside .minecraft for cheat JARs in known spots
    mc_dir = Path(os.environ.get("APPDATA", "")) / ".minecraft"
    for subdir_name in ("mods", "versions", "libraries"):
        subdir = mc_dir / subdir_name
        if not subdir.exists():
            continue
        try:
            for f in subdir.rglob("*.jar"):
                name_lower = f.name.lower()
                for sig in CHEAT_CLIENT_SIGNATURES["files"]:
                    # simple glob-like match (prefix wildcard)
                    clean_sig = sig.replace("*.jar", "").replace("*.exe", "")
                    if name_lower.startswith(clean_sig):
                        artifacts.append(CheatArtifact(
                            name=f.name,
                            path=str(f),
                            kind="file",
                            severity="High",
                        ))
                        break
        except PermissionError:
            pass

    return artifacts
