import tkinter as tk
import customtkinter as ctk
from hwh.core.tool_manager import TOOLS, ToolManager
from hwh.utils.helpers import THEME


class ToolsTab(ctk.CTkFrame):
    def __init__(self, parent, tool_manager: ToolManager, **kwargs):
        super().__init__(parent, fg_color=THEME["bg"], **kwargs)
        self.tm = tool_manager
        self._rows: dict[str, dict] = {}
        self._build()

    def _build(self):
        # Top bar
        bar = ctk.CTkFrame(self, fg_color=THEME["surface"], corner_radius=6)
        bar.pack(fill="x", padx=24, pady=(24, 12))

        ctk.CTkLabel(
            bar,
            text="ANALYSIS TOOLS",
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
            text_color=THEME["text"],
        ).pack(side="left", padx=16, pady=12)

        ctk.CTkButton(
            bar,
            text="Download All",
            width=130,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            command=self._download_all,
        ).pack(side="right", padx=12, pady=10)

        # Scrollable tool list
        scroll = ctk.CTkScrollableFrame(self, fg_color=THEME["bg"])
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        for tool in TOOLS:
            self._add_tool_row(scroll, tool)

        self.refresh_statuses()

    def _add_tool_row(self, parent, tool: dict):
        row = ctk.CTkFrame(parent, fg_color=THEME["surface"], corner_radius=6)
        row.pack(fill="x", pady=4)
        row.columnconfigure(1, weight=1)

        # Status dot
        dot = tk.Label(row, text="●", bg=THEME["surface"], fg=THEME["text_muted"], font=("Segoe UI", 14))
        dot.grid(row=0, column=0, padx=(14, 8), pady=14, sticky="n")

        # Name + description
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew", padx=0, pady=10)

        ctk.CTkLabel(
            info,
            text=tool["name"],
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=THEME["text"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            info,
            text=tool["description"],
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=THEME["text_dim"],
            anchor="w",
            wraplength=400,
        ).pack(anchor="w")

        # Progress bar (hidden initially)
        progress = ctk.CTkProgressBar(info, width=300, height=6, progress_color=THEME["accent"])
        progress.set(0)

        # Buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=12, pady=10)

        dl_btn = ctk.CTkButton(
            btn_frame,
            text="Download",
            width=100,
            fg_color=THEME["accent_soft"],
            hover_color=THEME["accent"],
            text_color=THEME["text"],
            command=lambda n=tool["name"]: self._download_one(n),
        )
        dl_btn.pack(pady=(0, 4))

        run_btn = ctk.CTkButton(
            btn_frame,
            text="Run",
            width=100,
            fg_color=THEME["surface2"],
            hover_color=THEME["border"],
            text_color=THEME["text_dim"],
            state="disabled",
            command=lambda n=tool["name"]: self._run_tool(n),
        )
        run_btn.pack()

        self._rows[tool["name"]] = {
            "dot": dot,
            "dl_btn": dl_btn,
            "run_btn": run_btn,
            "progress": progress,
            "info_frame": info,
        }

    def refresh_statuses(self):
        for status in self.tm.get_all_statuses():
            row = self._rows.get(status.name)
            if not row:
                continue
            if status.downloaded:
                row["dot"].configure(fg=THEME["green"])
                row["dl_btn"].configure(state="disabled", text="Downloaded")
                row["run_btn"].configure(state="normal", fg_color=THEME["accent"], text_color=THEME["text"])
            elif status.downloading:
                row["dot"].configure(fg=THEME["yellow"])
                row["dl_btn"].configure(state="disabled", text="Downloading…")
            else:
                row["dot"].configure(fg=THEME["text_muted"])
                row["dl_btn"].configure(state="normal", text="Download")
                row["run_btn"].configure(state="disabled")

    def _download_one(self, name: str):
        row = self._rows[name]
        row["progress"].pack(anchor="w", pady=(4, 0))
        row["progress"].set(0)

        def on_progress(pct):
            self.after(0, lambda: row["progress"].set(pct / 100))

        def on_done(ok, err):
            def _update():
                row["progress"].pack_forget()
                self.refresh_statuses()
                if not ok:
                    row["dot"].configure(fg=THEME["red"])
            self.after(0, _update)

        self.tm.download_tool(name, on_progress=on_progress, on_done=on_done)
        self.refresh_statuses()

    def _download_all(self):
        for name in self._rows:
            status = self.tm.statuses.get(name)
            if status and not status.downloaded:
                self._download_one(name)

    def _run_tool(self, name: str):
        ok, err = self.tm.run_tool(name)
        if not ok:
            row = self._rows[name]
            row["dot"].configure(fg=THEME["red"])
