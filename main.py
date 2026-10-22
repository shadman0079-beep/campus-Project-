
# main.py
# Main entry point for BubtOps

import tkinter as tk
from tkinter import messagebox

from database.db import setup_database
from screens.loading_screen import show_loading
from screens.dashboard import show_dashboard


def finish_startup():
    """Prepare the database and open the dashboard."""

    try:
        setup_database()
        show_dashboard(window)

    except Exception as error:
        messagebox.showerror(
            "BubtOps Startup Error",
            f"Could not start BubtOps:\n\n{error}",
            parent=window
        )
        window.destroy()


def main():
    """Start the BubtOps application."""

    global window

    window = tk.Tk()

    # Show the loading screen first.
    show_loading(window, finish_startup)

    # Keep the application running.
    window.mainloop()


if __name__ == "__main__":
    main()
