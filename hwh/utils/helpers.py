from pathlib import Path

THEME = {
    "bg":           "#090909",
    "surface":      "#111111",
    "surface2":     "#191919",
    "border":       "#2b1719",
    "accent":       "#e3262e",
    "accent_hover": "#ff3942",
    "accent_soft":  "#4d171b",
    "green":        "#22c55e",
    "yellow":       "#facc15",
    "red":          "#ef4444",
    "text":         "#f1f1f3",
    "text_dim":     "#a7a0a1",
    "text_muted":   "#665e60",
    "font":         ("Segoe UI", 12),
    "font_sm":      ("Segoe UI", 10),
    "font_lg":      ("Segoe UI", 14, "bold"),
    "font_xl":      ("Segoe UI", 18, "bold"),
    "font_mono":    ("Consolas", 10),
}


def severity_color(severity: str) -> str:
    return {
        "High":   THEME["red"],
        "Medium": THEME["yellow"],
        "Low":    THEME["green"],
    }.get(severity, THEME["text_dim"])


def truncate(text: str, max_len: int = 60) -> str:
    return text if len(text) <= max_len else "…" + text[-(max_len - 1):]
