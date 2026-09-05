import threading
import customtkinter as ctk
from hwh.core import minecraft_detector
from hwh.utils.helpers import THEME, severity_color, truncate


class MinecraftTab(ctk.CTkFrame):
    def __init__(self, parent, on_scan_done=None, **kwargs):
        super().__init__(parent, fg_color=THEME["bg"], **kwargs)
        self.on_scan_done = on_scan_done
        self._build()

    def _build(self):
        # Top bar
        bar = ctk.CTkFrame(self, fg_color=THEME["surface"], corner_radius=6)
        bar.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            bar,
            text="MINECRAFT SCANNER",
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
            text_color=THEME["text"],
        ).pack(side="left", padx=16, pady=12)

        self.scan_btn = ctk.CTkButton(
            bar,
            text="Run Scan",
            width=110,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            command=self._run_scan,
        )
        self.scan_btn.pack(side="right", padx=12, pady=10)

        self.status_label = ctk.CTkLabel(
            bar,
            text="Ready",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=THEME["text_dim"],
        )
        self.status_label.pack(side="right", padx=6)

        # Columns layout
        columns = ctk.CTkFrame(self, fg_color="transparent")
        columns.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        columns.columnconfigure(0, weight=1)
        columns.columnconfigure(1, weight=1)

        # Left: accounts
        self.accounts_frame = self._section(columns, "Minecraft Accounts", 0)

        # Right: artifacts
        self.cheats_frame = self._section(columns, "Cheat Artifacts", 1)

        # Bottom: installations
        self.installs_frame = self._section_bottom(columns, "Installations Detected")

        self._show_placeholder(self.accounts_frame, "Click 'Run Scan' to detect accounts.")
        self._show_placeholder(self.cheats_frame, "Click 'Run Scan' to check for cheat clients.")
        self._show_placeholder(self.installs_frame, "")

    def _section(self, parent, title: str, col: int) -> ctk.CTkScrollableFrame:
        wrapper = ctk.CTkFrame(parent, fg_color=THEME["surface"], corner_radius=10)
        wrapper.grid(row=0, column=col, sticky="nsew", padx=(0 if col else 0, 5 if col == 0 else 0),
                     pady=4, ipadx=0)

        ctk.CTkLabel(
            wrapper,
            text=title,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=THEME["text"],
        ).pack(anchor="w", padx=14, pady=(12, 6))

        ctk.CTkFrame(wrapper, height=1, fg_color=THEME["border"]).pack(fill="x", padx=12)

        scroll = ctk.CTkScrollableFrame(wrapper, fg_color="transparent", height=260)
        scroll.pack(fill="both", expand=True, padx=4, pady=4)
        return scroll

    def _section_bottom(self, parent, title: str) -> ctk.CTkScrollableFrame:
        wrapper = ctk.CTkFrame(parent, fg_color=THEME["surface"], corner_radius=10)
        wrapper.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))

        ctk.CTkLabel(
            wrapper,
            text=title,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=THEME["text"],
        ).pack(anchor="w", padx=14, pady=(12, 6))

        ctk.CTkFrame(wrapper, height=1, fg_color=THEME["border"]).pack(fill="x", padx=12)

        scroll = ctk.CTkScrollableFrame(wrapper, fg_color="transparent", height=100)
        scroll.pack(fill="both", expand=True, padx=4, pady=4)
        return scroll

    def _show_placeholder(self, parent, text: str):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=THEME["text_muted"],
        ).pack(pady=20)

    def _run_scan(self):
        self.scan_btn.configure(state="disabled", text="Scanning…")
        self.status_label.configure(text="Scanning…", text_color=THEME["yellow"])
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        result = minecraft_detector.scan()
        self.after(0, lambda: self._display_results(result))

    def _display_results(self, result):
        self._clear(self.accounts_frame)
        self._clear(self.cheats_frame)
        self._clear(self.installs_frame)

        # Accounts
        if result.accounts:
            for acc in result.accounts:
                self._account_card(self.accounts_frame, acc)
        else:
            self._show_placeholder(self.accounts_frame, "No accounts found.")

        # Cheat artifacts
        if result.cheat_artifacts:
            for art in result.cheat_artifacts:
                self._artifact_card(self.cheats_frame, art)
        else:
            ctk.CTkLabel(
                self.cheats_frame,
                text="✓  No cheat artifacts detected.",
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=THEME["green"],
            ).pack(pady=20)

        # Installations
        if result.installations:
            for path in result.installations:
                ctk.CTkLabel(
                    self.installs_frame,
                    text=path,
                    font=ctk.CTkFont("Consolas", 10),
                    text_color=THEME["text_dim"],
                    anchor="w",
                ).pack(anchor="w", padx=10, pady=2)
        else:
            self._show_placeholder(self.installs_frame, "No Minecraft installations found.")

        # Update status
        cheats = len(result.cheat_artifacts)
        summary = f"Done — {len(result.accounts)} account(s), {cheats} artifact(s)"
        color = THEME["red"] if cheats else THEME["green"]
        self.status_label.configure(text=summary, text_color=color)
        self.scan_btn.configure(state="normal", text="Run Scan")

        if self.on_scan_done:
            self.on_scan_done(result)

    def _account_card(self, parent, acc):
        card = ctk.CTkFrame(parent, fg_color=THEME["surface2"], corner_radius=8)
        card.pack(fill="x", padx=4, pady=3)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            top,
            text=acc.username,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=THEME["text"],
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=acc.account_type,
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=THEME["accent"],
        ).pack(side="right")

        if acc.uuid:
            ctk.CTkLabel(
                card,
                text=f"UUID: {acc.uuid}",
                font=ctk.CTkFont("Consolas", 9),
                text_color=THEME["text_muted"],
                anchor="w",
            ).pack(anchor="w", padx=10, pady=(0, 6))

    def _artifact_card(self, parent, art):
        card = ctk.CTkFrame(parent, fg_color=THEME["surface2"], corner_radius=8)
        card.pack(fill="x", padx=4, pady=3)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(
            top,
            text=art.name,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=severity_color(art.severity),
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=art.severity,
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=severity_color(art.severity),
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text=truncate(art.path, 55),
            font=ctk.CTkFont("Consolas", 9),
            text_color=THEME["text_muted"],
            anchor="w",
        ).pack(anchor="w", padx=10, pady=(0, 6))

    def _clear(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
