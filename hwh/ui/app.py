import customtkinter as ctk
from hwh.core.tool_manager import ToolManager
from hwh.ui.tabs.overview_tab import OverviewTab
from hwh.ui.tabs.tools_tab import ToolsTab
from hwh.utils.helpers import THEME


class HWHApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("hwh tool")
        self.geometry("980x680")
        self.minsize(820, 580)
        self.configure(fg_color=THEME["bg"])

        self.tool_manager = ToolManager()
        self._build()

    def _build(self):
        # Sidebar
        sidebar = ctk.CTkFrame(self, fg_color=THEME["surface"], width=210, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="hwh tool",
            font=ctk.CTkFont("Segoe UI", 21, "bold"),
            text_color=THEME["accent"],
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            sidebar,
            text="system analysis suite",
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=THEME["text_muted"],
        ).pack(pady=(0, 24))

        ctk.CTkFrame(sidebar, height=1, fg_color=THEME["accent"]).pack(fill="x", padx=16, pady=(0, 16))

        # Content area
        self.content = ctk.CTkFrame(self, fg_color=THEME["bg"], corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)

        # Build tabs
        self.overview_tab = OverviewTab(self.content, self.tool_manager)
        self.tools_tab = ToolsTab(self.content, self.tool_manager)

        self._tabs = {
            "Overview":  self.overview_tab,
            "Tools":     self.tools_tab,
        }

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for name in self._tabs:
            btn = ctk.CTkButton(
                sidebar,
                text=name.upper(),
                fg_color="transparent",
                hover_color=THEME["surface2"],
                text_color=THEME["text_dim"],
                anchor="w",
                height=40,
                corner_radius=6,
                border_spacing=12,
                command=lambda n=name: self._switch_tab(n),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_buttons[name] = btn

        # Version at bottom
        ctk.CTkLabel(
            sidebar,
            text="v2.0.0",
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=THEME["text_muted"],
        ).pack(side="bottom", pady=16)

        self._switch_tab("Overview")

    def _switch_tab(self, name: str):
        for tab in self._tabs.values():
            tab.pack_forget()

        self._tabs[name].pack(fill="both", expand=True)

        for n, btn in self._nav_buttons.items():
            if n == name:
                btn.configure(
                    fg_color=THEME["accent_soft"],
                    text_color=THEME["text"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=THEME["text_dim"],
                )

def run():
    app = HWHApp()
    app.mainloop()
