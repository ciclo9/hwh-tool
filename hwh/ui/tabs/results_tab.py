import datetime
import customtkinter as ctk
from hwh.utils.helpers import THEME


class ResultsTab(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=THEME["bg"], **kwargs)
        self._build()
        self._mc_result = None

    def _build(self):
        bar = ctk.CTkFrame(self, fg_color=THEME["surface"], corner_radius=10)
        bar.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            bar,
            text="Investigation Report",
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
            text_color=THEME["text"],
        ).pack(side="left", padx=16, pady=12)

        ctk.CTkButton(
            bar,
            text="Copy Report",
            width=110,
            fg_color=THEME["accent_soft"],
            hover_color=THEME["accent"],
            text_color=THEME["text"],
            command=self._copy_report,
        ).pack(side="right", padx=12, pady=10)

        self.textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont("Consolas", 11),
            fg_color=THEME["surface"],
            text_color=THEME["text"],
            border_width=0,
            corner_radius=10,
            wrap="word",
        )
        self.textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.textbox.configure(state="disabled")

        self._write("No scan has been run yet.\nRun a scan from the Minecraft tab first.")

    def update_from_minecraft(self, mc_result):
        self._mc_result = mc_result
        report = self._build_report(mc_result)
        self._write(report)

    def _build_report(self, mc_result) -> str:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "=" * 60,
            "  hwh tool - investigation report",
            f"  Generated: {now}",
            "=" * 60,
            "",
        ]

        # Accounts section
        lines.append("[ MINECRAFT ACCOUNTS ]")
        if mc_result.accounts:
            for acc in mc_result.accounts:
                lines.append(f"  Username   : {acc.username}")
                lines.append(f"  Type       : {acc.account_type}")
                if acc.uuid:
                    lines.append(f"  UUID       : {acc.uuid}")
                lines.append(f"  Source     : {acc.source}")
                lines.append("")
        else:
            lines.append("  No accounts detected.")
            lines.append("")

        # Installations
        lines.append("[ MINECRAFT INSTALLATIONS ]")
        if mc_result.installations:
            for path in mc_result.installations:
                lines.append(f"  {path}")
        else:
            lines.append("  None found.")
        lines.append("")

        # Cheat artifacts
        lines.append("[ CHEAT ARTIFACTS ]")
        if mc_result.cheat_artifacts:
            for art in mc_result.cheat_artifacts:
                lines.append(f"  [!] {art.name}")
                lines.append(f"      Kind     : {art.kind}")
                lines.append(f"      Path     : {art.path}")
                lines.append(f"      Severity : {art.severity}")
                lines.append("")
        else:
            lines.append("  No cheat artifacts found. ✓")
            lines.append("")

        # Verdict
        lines.append("[ VERDICT ]")
        cheats = len(mc_result.cheat_artifacts)
        if cheats == 0:
            lines.append("  CLEAN — No cheat client artifacts detected.")
        elif cheats <= 2:
            lines.append(f"  SUSPICIOUS — {cheats} artifact(s) found. Manual review recommended.")
        else:
            lines.append(f"  LIKELY CHEATING — {cheats} artifact(s) found.")
        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _write(self, text: str):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.textbox.configure(state="disabled")

    def _copy_report(self):
        content = self.textbox.get("1.0", "end")
        self.clipboard_clear()
        self.clipboard_append(content)
