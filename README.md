<<<<<<< HEAD
# hwh-tool
=======
# hwh tool v2.0

Desktop GUI for investigating potential Minecraft cheaters on Windows.
- **Minecraft Account Detection** — reads launcher JSON files to list all local accounts (username, UUID, type)
- **Cheat Client Artifact Scanner** — detects folders/JARs from known clients: Wurst, Meteor, Impact, LiquidBounce, Vanta, Sigma, Aristois, Inertia, Future, RusherHack, Raven, Novoline, and more
- **Forensic Tool Launcher** — download and run BAM Parser, Paths Parser, JournalTrace, Kernel Live Dump Analyzer, espouken, Last Activity View, ADS Viewer, WinPrefetchView
- **Investigation Report** — auto-generated copyable report with verdict

## Setup

```bash
pip install -r requirements.txt
python main.py
```

> Requires Windows. Run as Administrator for full registry and prefetch access.

## Structure

```
hwh/
├── core/
│   ├── tool_manager.py       # Download + launch external tools
│   ├── minecraft_detector.py # Account + cheat artifact detection
│   └── system_scanner.py     # Startup entries + temp dir scan
├── ui/
│   ├── app.py                # Main window + sidebar navigation
│   └── tabs/
│       ├── overview_tab.py   # Dashboard with stat cards
│       ├── tools_tab.py      # Tool download/run panel
│       ├── minecraft_tab.py  # Account + artifact scanner
│       └── results_tab.py    # Report viewer
└── utils/

- Run as **Administrator** for full access to prefetch, registry, and protected paths.
- Use **BAM Parser** and **JournalTrace** for the strongest execution history evidence.
- Use **WinPrefetchView** to verify if a cheat executable was ever launched.
- Use **ADS Viewer** to detect hidden files masquerading as legitimate ones.
>>>>>>> 40c9d21 (Improve hwh tool GUI)
