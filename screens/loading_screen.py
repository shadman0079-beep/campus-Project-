
# screens/loading_screen.py

import tkinter as tk
import theme


def show_loading(window, on_complete):
    """Display the BubtOps loading animation."""

    window.title("BubtOps")
    window.geometry("650x420")
    window.resizable(False, False)
    window.configure(bg=theme.BACKGROUND)

    window.update_idletasks()

    screen_x = (window.winfo_screenwidth() - 650) // 2
    screen_y = (window.winfo_screenheight() - 420) // 2
    window.geometry(f"650x420+{screen_x}+{screen_y}")

    # Geometric emblem
    emblem = tk.Canvas(
        window,
        width=76,
        height=76,
        bg=theme.BACKGROUND,
        highlightthickness=0
    )
    emblem.pack(pady=(48, 8))

    blocks = [
        emblem.create_rectangle(
            12, 12, 32, 32, fill=theme.PRIMARY, outline=""
        ),
        emblem.create_rectangle(
            38, 12, 58, 32,
            fill=theme.PROGRESS_TRACK, outline=""
        ),
        emblem.create_rectangle(
            12, 38, 32, 58,
            fill=theme.PROGRESS_TRACK, outline=""
        ),
        emblem.create_rectangle(
            38, 38, 58, 58, fill=theme.PRIMARY, outline=""
        )
    ]

    tk.Label(
        window,
        text="BubtOps",
        font=(theme.FONT_FAMILY, theme.TITLE_SIZE, "bold"),
        bg=theme.BACKGROUND,
        fg=theme.NAVY
    ).pack(pady=(0, 3))

    tk.Label(
        window,
        text="University Asset Maintenance System",
        font=(theme.FONT_FAMILY, theme.BODY_SIZE),
        bg=theme.BACKGROUND,
        fg=theme.TEXT_MUTED
    ).pack()

    # Custom progress bar
    bar = tk.Canvas(
        window,
        width=320,
        height=8,
        bg=theme.BACKGROUND,
        highlightthickness=0
    )
    bar.pack(pady=(30, 8))

    bar.create_rectangle(
        0, 1, 320, 7,
        fill=theme.PROGRESS_TRACK,
        outline=""
    )

    fill = bar.create_rectangle(
        0, 1, 0, 7,
        fill=theme.PRIMARY,
        outline=""
    )

    percentage = tk.Label(
        window,
        text="00%",
        font=(theme.FONT_FAMILY, theme.BODY_SIZE, "bold"),
        bg=theme.BACKGROUND,
        fg=theme.NAVY
    )
    percentage.pack()

    status = tk.Label(
        window,
        text="Preparing your workspace",
        font=(theme.FONT_FAMILY, theme.BODY_SIZE),
        bg=theme.BACKGROUND,
        fg=theme.TEXT_MUTED
    )
    status.pack(pady=(5, 12))

    tk.Label(
        window,
        text="OFFLINE SYSTEM   •   LOCAL DATA",
        font=(theme.FONT_FAMILY, theme.SMALL_SIZE, "bold"),
        bg=theme.BACKGROUND,
        fg="#98A4B5"
    ).pack()

    value = 0

    def animate():
        nonlocal value

        if not window.winfo_exists():
            return

        value = min(value + 1, 100)

        bar.coords(fill, 0, 1, 3.2 * value, 7)
        percentage.config(text=f"{value:02d}%")

        active_block = (value // 6) % 4

        for index, block in enumerate(blocks):
            emblem.itemconfig(
                block,
                fill=(
                    theme.PRIMARY
                    if index == active_block
                    else theme.PROGRESS_TRACK
                )
            )

        if value < 30:
            status.config(text="Preparing your workspace")
        elif value < 60:
            status.config(text="Organizing campus systems")
        elif value < 90:
            status.config(text="Setting up your workspace")
        else:
            status.config(text="Almost ready")

        if value < 100:
            window.after(22, animate)
        else:
            percentage.config(text="READY")
            status.config(text="Welcome to BubtOps")

            window.after(450, on_complete)

    window.after(22, animate)
