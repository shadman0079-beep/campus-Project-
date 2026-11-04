
# icons.py
# Central Lucide icon manager for BubtOps

from tkinter_icons import LucideIcon


def get_icon(name, size=22, color="#55C8FF"):
    """
    Create a Lucide icon.
    Call this only after the main Tkinter window exists.
    """

    icon = LucideIcon(
        name,
        size=size,
        color=color
    )

    return icon.image
