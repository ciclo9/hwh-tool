import os
import subprocess
import threading
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable, Optional

TOOLS_DIR = Path(__file__).parent.parent.parent / "tools"

TOOLS = [
    {
        "name": "BAM Parser",
        "file": "BAMParser.exe",
        "url": "https://github.com/spokwn/BAM-parser/releases/download/v1.2.9/BAMParser.exe",
        "description": "Parses Background Activity Monitor — reveals recently executed programs.",
        "args": [],
    },
    {
        "name": "Paths Parser",
        "file": "PathsParser.exe",
        "url": "https://github.com/spokwn/PathsParser/releases/download/v1.2/PathsParser.exe",
        "description": "Extracts recently accessed file paths from registry & logs.",
        "args": [],
    },
    {
        "name": "JournalTrace",
        "file": "JournalTrace.exe",
        "url": "https://github.com/spokwn/JournalTrace/releases/download/1.2/JournalTrace.exe",
        "description": "Reads the NTFS USN journal — tracks file creation/deletion history.",
        "args": [],
    },
    {
        "name": "Kernel Live Dump Analyzer",
        "file": "KernelLiveDump.exe",
        "url": "https://github.com/spokwn/KernelLiveDumpTool/releases/download/v1.1/KernelLiveDump.exe",
        "description": "Analyzes kernel live dumps for hidden modules and suspicious drivers.",
        "args": [],
    },
    {
        "name": "espouken (Multi-Tool)",
        "file": "espouken.exe",
        "url": "https://github.com/spokwn/Tool/releases/download/v1.1.3/espouken.exe",
        "description": "All-in-one forensic tool for cheat artifact detection.",
        "args": [],
    },
    {
        "name": "Last Activity View",
        "file": "LastActivityView.exe",
        "url": "https://www.nirsoft.net/utils/lastactivityview.zip",
        "description": "Shows a timeline of user activity (program runs, file opens, shutdowns).",
        "args": [],
        "zip": True,
        "zip_target": "LastActivityView.exe",
    },
    {
        "name": "Alternate Stream View (ADS)",
        "file": "AlternateStreamView.exe",
        "url": "https://www.nirsoft.net/utils/alternatestreamview-x64.zip",
        "description": "Detects hidden NTFS Alternate Data Streams — common cheat hiding technique.",
        "args": [],
        "zip": True,
        "zip_target": "AlternateStreamView.exe",
    },
    {
        "name": "WinPrefetchView",
        "file": "WinPrefetchView.exe",
        "url": "https://www.nirsoft.net/utils/winprefetchview-x64.zip",
        "description": "Reads Windows Prefetch files — shows execution history of programs.",
        "args": [],
        "zip": True,
        "zip_target": "WinPrefetchView.exe",
    },
]


@dataclass
class ToolStatus:
    name: str
    file: str
    downloaded: bool = False
    downloading: bool = False
    error: Optional[str] = None
    progress: int = 0


class ToolManager:
    def __init__(self):
        TOOLS_DIR.mkdir(exist_ok=True)
        self.statuses: dict[str, ToolStatus] = {
            t["name"]: ToolStatus(name=t["name"], file=t["file"]) for t in TOOLS
        }
        self._refresh_status()

    def _refresh_status(self):
        for tool in TOOLS:
            path = TOOLS_DIR / tool["file"]
            self.statuses[tool["name"]].downloaded = path.exists()

    def get_tool_path(self, name: str) -> Optional[Path]:
        tool = next((t for t in TOOLS if t["name"] == name), None)
        if not tool:
            return None
        path = TOOLS_DIR / tool["file"]
        return path if path.exists() else None

    def download_tool(
        self,
        tool_name: str,
        on_progress: Optional[Callable[[int], None]] = None,
        on_done: Optional[Callable[[bool, str], None]] = None,
    ):
        tool = next((t for t in TOOLS if t["name"] == tool_name), None)
        if not tool:
            return

        status = self.statuses[tool_name]
        status.downloading = True
        status.error = None

        def _download():
            try:
                dest = TOOLS_DIR / tool["file"]
                url = tool["url"]
                is_zip = tool.get("zip", False)

                if is_zip:
                    import zipfile
                    import io

                    zip_path = TOOLS_DIR / f"_temp_{tool['file']}.zip"
                    _download_file(url, zip_path, on_progress)
                    with zipfile.ZipFile(zip_path, "r") as z:
                        target = tool.get("zip_target", tool["file"])
                        with z.open(target) as src, open(dest, "wb") as dst:
                            dst.write(src.read())
                    zip_path.unlink(missing_ok=True)
                else:
                    _download_file(url, dest, on_progress)

                status.downloaded = True
                status.downloading = False
                if on_done:
                    on_done(True, "")
            except Exception as e:
                status.error = str(e)
                status.downloading = False
                if on_done:
                    on_done(False, str(e))

        threading.Thread(target=_download, daemon=True).start()

    def download_all(
        self,
        on_tool_done: Optional[Callable[[str, bool, str], None]] = None,
        on_all_done: Optional[Callable[[], None]] = None,
    ):
        pending = [t for t in TOOLS if not (TOOLS_DIR / t["file"]).exists()]
        if not pending:
            if on_all_done:
                on_all_done()
            return

        completed = [0]

        def _done(name, success, error):
            completed[0] += 1
            if on_tool_done:
                on_tool_done(name, success, error)
            if completed[0] >= len(pending) and on_all_done:
                on_all_done()

        for tool in pending:
            self.download_tool(
                tool["name"],
                on_done=lambda ok, err, n=tool["name"]: _done(n, ok, err),
            )

    def run_tool(self, tool_name: str) -> tuple[bool, str]:
        path = self.get_tool_path(tool_name)
        if not path:
            return False, "Tool not downloaded."
        try:
            subprocess.Popen([str(path)], cwd=str(TOOLS_DIR))
            return True, ""
        except Exception as e:
            return False, str(e)

    def get_all_statuses(self) -> list[ToolStatus]:
        self._refresh_status()
        return list(self.statuses.values())


def _download_file(url: str, dest: Path, on_progress=None):
    req = urllib.request.Request(url, headers={"User-Agent": "HWH-Tool/2.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk = 8192
        with open(dest, "wb") as f:
            while True:
                data = resp.read(chunk)
                if not data:
                    break
                f.write(data)
                downloaded += len(data)
                if total and on_progress:
                    on_progress(int(downloaded / total * 100))
    if on_progress:
        on_progress(100)
