
# theme.py
# Central theme system for BubtOps

import json
from pathlib import Path

# --------------------------------------------------
# THEME SETTINGS
# --------------------------------------------------

THEME_FILE = Path(__file__).resolve().parent / "bubtops_settings.json"

THEMES = {
    "Midnight Blue": {
        "BACKGROUND": "#0B1526",
        "SURFACE": "#101D32",
        "CARD": "#11213A",
        "ACCENT": "#2B82FF",
        "SECONDARY": "#19C7E8",
        "TEXT": "#F3F6FF",
    },
    "Midnight Gold": {
        "BACKGROUND": "#323437",
        "SURFACE": "#2C2E31",
        "CARD": "#3A3C40",
        "ACCENT": "#E2B714",
        "SECONDARY": "#D1D0C5",
        "TEXT": "#E6E6E6",
    },
    "Arctic Pulse": {
        "BACKGROUND": "#101C2C",
        "SURFACE": "#17283D",
        "CARD": "#1D3048",
        "ACCENT": "#45D6E8",
        "SECONDARY": "#3C91C9",
        "TEXT": "#E7F0FA",
    },
    "Violet Haze": {
        "BACKGROUND": "#191526",
        "SURFACE": "#241D35",
        "CARD": "#2D2442",
        "ACCENT": "#B69CFF",
        "SECONDARY": "#E09AFF",
        "TEXT": "#F0EBFA",
    },
    "Dracula": {
        "BACKGROUND": "#282A36",
        "SURFACE": "#21222C",
        "CARD": "#343746",
        "ACCENT": "#BD93F9",
        "SECONDARY": "#8BE9FD",
        "TEXT": "#F8F8F2",
    },
    "Nord": {
        "BACKGROUND": "#2E3440",
        "SURFACE": "#272D36",
        "CARD": "#3B4252",
        "ACCENT": "#88C0D0",
        "SECONDARY": "#81A1C1",
        "TEXT": "#ECEFF4",
    },
    "Rosé Pine": {
        "BACKGROUND": "#191724",
        "SURFACE": "#1F1D2E",
        "CARD": "#26233A",
        "ACCENT": "#EBBCBA",
        "SECONDARY": "#C4A7E7",
        "TEXT": "#E0DEF4",
    },
    "Gruvbox": {
        "BACKGROUND": "#282828",
        "SURFACE": "#1D2021",
        "CARD": "#3C3836",
        "ACCENT": "#FABD2F",
        "SECONDARY": "#8EC07C",
        "TEXT": "#EBDBB2",
    },
    "Catppuccin Mocha": {
        "BACKGROUND": "#1E1E2E",
        "SURFACE": "#181825",
        "CARD": "#313244",
        "ACCENT": "#CBA6F7",
        "SECONDARY": "#89DCEB",
        "TEXT": "#CDD6F4",
    },
    "Forest": {
        "BACKGROUND": "#14231D",
        "SURFACE": "#192D25",
        "CARD": "#203B30",
        "ACCENT": "#65D6A0",
        "SECONDARY": "#B7D98B",
        "TEXT": "#E6F4EC",
    },
    "Sunset": {
        "BACKGROUND": "#291B26",
        "SURFACE": "#36212D",
        "CARD": "#472B36",
        "ACCENT": "#FF9B71",
        "SECONDARY": "#FFC66D",
        "TEXT": "#FFF0E8",
    },
    "Light Mode": {
        "BACKGROUND": "#F1F5FA",
        "SURFACE": "#E5ECF5",
        "CARD": "#FFFFFF",
        "ACCENT": "#3478F6",
        "SECONDARY": "#087E8B",
        "TEXT": "#182338",
    },
}

# --------------------------------------------------
# ACTIVE THEME
# --------------------------------------------------

DEFAULT_THEME = "Midnight Blue"
ACTIVE_THEME_NAME = DEFAULT_THEME


def load_saved_theme():
    """Load the previously selected theme, if available."""
    global ACTIVE_THEME_NAME

    try:
        if THEME_FILE.exists():
            settings = json.loads(THEME_FILE.read_text(encoding="utf-8"))
            name = settings.get("theme")

            if name in THEMES:
                ACTIVE_THEME_NAME = name
    except (OSError, json.JSONDecodeError):
        ACTIVE_THEME_NAME = DEFAULT_THEME


def save_theme(name):
    """Save the selected theme for the next launch."""
    try:
        THEME_FILE.write_text(
            json.dumps({"theme": name}, indent=4),
            encoding="utf-8",
        )
        return True
    except OSError:
        return False


def get_theme(name=None):
    """Return a theme's palette."""
    return THEMES.get(name or ACTIVE_THEME_NAME, THEMES[DEFAULT_THEME]).copy()


def apply_theme(name):
    """Set the active theme and update shared color constants."""
    global ACTIVE_THEME_NAME
    global BACKGROUND, DASHBOARD_BACKGROUND, SIDEBAR_BACKGROUND
    global HEADER_BACKGROUND, CARD_BACKGROUND, CARD_BACKGROUND_ALT
    global TABLE_BACKGROUND, PRIMARY, CYAN, PURPLE, NAVY
    global TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, DASHBOARD_TEXT
    global SUCCESS, WARNING, ERROR, INFO, PROGRESS_TRACK
    global BORDER, DIVIDER

    if name not in THEMES:
        return False

    ACTIVE_THEME_NAME = name
    palette = THEMES[name]

    BACKGROUND = palette["BACKGROUND"]
    DASHBOARD_BACKGROUND = palette["BACKGROUND"]
    SIDEBAR_BACKGROUND = palette["SURFACE"]
    HEADER_BACKGROUND = palette["SURFACE"]
    CARD_BACKGROUND = palette["CARD"]
    CARD_BACKGROUND_ALT = palette["SURFACE"]
    TABLE_BACKGROUND = palette["CARD"]

    PRIMARY = palette["ACCENT"]
    CYAN = palette["SECONDARY"]
    PURPLE = palette["ACCENT"]
    NAVY = palette["SURFACE"]

    TEXT_PRIMARY = palette["TEXT"]
    TEXT_SECONDARY = palette["TEXT"]
    TEXT_MUTED = "#A9BCD8" if name != "Light Mode" else "#65748B"
    DASHBOARD_TEXT = TEXT_SECONDARY

    SUCCESS = "#19C99A"
    WARNING = "#FFAD42"
    ERROR = "#FF647C"
    INFO = PRIMARY

    PROGRESS_TRACK = palette["SURFACE"]
    BORDER = palette["SURFACE"]
    DIVIDER = palette["CARD"]

    return True


# --------------------------------------------------
# TYPOGRAPHY AND LAYOUT
# --------------------------------------------------

FONT_FAMILY = "Segoe UI"
TITLE_SIZE = 29
HEADING_SIZE = 18
BODY_SIZE = 10
SMALL_SIZE = 8

SIDEBAR_WIDTH = 250
HEADER_HEIGHT = 100
CARD_RADIUS = 12


# Load preferences before the app imports these constants.
load_saved_theme()
apply_theme(ACTIVE_THEME_NAME)
