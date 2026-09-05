import tkinter as tk
import customtkinter as ctk
from hwh.utils.helpers import THEME


class OverviewTab(ctk.CTkFrame):
    def __init__(self, parent, tool_manager, **kwargs):
        super().__init__(parent, fg_color=THEME["bg"], **kwargs)
        self.tool_manager = tool_manager
        self._build()

    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=THEME["surface"], corner_radius=6)
        header.pack(fill="x", padx=24, pady=(24, 12))

        ctk.CTkLabel(
            header,
            text="hwh tool",
            font=ctk.CTkFont("Segoe UI", 24, "bold"),
            text_color=THEME["text"],
        ).pack(side="left", padx=20, pady=18)

        ctk.CTkLabel(
            header,
            text="SYSTEM OVERVIEW  /  v2.0",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=THEME["text_dim"],
        ).pack(side="left", padx=0, pady=18)

        # Stat cards row
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=18, pady=6)

        self.stat_tools = self._stat_card("Tools Downloaded", "-", THEME["accent"])
        self.stat_available = self._stat_card("Tools Available", str(len(self.tool_manager.get_all_statuses())), THEME["green"])
        self.stat_ready = self._stat_card("Ready To Run", "-", THEME["yellow"])

        # Instructions
        info = ctk.CTkFrame(self, fg_color=THEME["surface"], corner_radius=6)
        info.pack(fill="x", padx=24, pady=12)

        ctk.CTkLabel(
            info,
            text="GETTING STARTED",
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            text_color=THEME["text"],
        ).pack(anchor="w", padx=16, pady=(14, 4))

        steps = [
            "1.  Open TOOLS and review the available analysis tools.",
            "2.  Download the tools you need for your investigation.",
            "3.  Run a downloaded tool from its action panel.",
            "4.  Return here to track your tool readiness.",
        ]
        for step in steps:
            ctk.CTkLabel(
                info,
                text=step,
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=THEME["text_dim"],
                anchor="w",
            ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkFrame(info, height=12, fg_color="transparent").pack()

    def _stat_card(self, label: str, value: str, color: str) -> ctk.CTkLabel:
        card = ctk.CTkFrame(self.stats_frame, fg_color=THEME["surface"], corner_radius=6)
        card.pack(side="left", expand=True, fill="both", padx=6, pady=5)

        val_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont("Segoe UI", 28, "bold"),
            text_color=color,
        )
        val_label.pack(pady=(16, 2))

        ctk.CTkLabel(
            card,
            text=label,
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=THEME["text_dim"],
        ).pack(pady=(0, 14))

        return val_label

    def update_stats(self, tools_ok: int, accounts: int = 0, cheats: int = 0, startups: int = 0):
        self.stat_tools.configure(text=str(tools_ok))
        self.stat_ready.configure(text=str(tools_ok))
