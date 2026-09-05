# hwh tool v2.0

Desktop GUI for managing and running Windows system analysis tools.

## Features

- Forensic tool launcher for Windows analysis utilities
- Tool readiness dashboard for downloaded and runnable tools
- Focused Overview and Tools workflows with a red and black theme

## Setup

```bash
pip install -r requirements.txt
python main.py
```

Requires Windows. Run as Administrator for full registry and prefetch access.

## Structure

```
hwh/
├── core/
│   ├── tool_manager.py       # Download and launch external tools
│   └── system_scanner.py     # Startup entries and temp directory scan
├── ui/
│   ├── app.py                # Main window and sidebar navigation
│   └── tabs/
│       ├── overview_tab.py   # Dashboard with tool stats
│       ├── tools_tab.py      # Tool download and run panel
│       ├── minecraft_tab.py  # Legacy scanner module
│       └── results_tab.py    # Legacy report module
└── utils/
    └── helpers.py            # Theme constants and utilities
```

## Tips

- Run as Administrator for full access to protected paths.
- Use the Tools view to download and launch analysis utilities.
