# screens/dashboard.py
# BubtOps - University Asset Maintenance System

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

import theme
from database.db import DATABASE_PATH


def get_dashboard_data():
    """Read dashboard statistics and recent maintenance records."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        total_assets = connection.execute(
            "SELECT COUNT(*) FROM assets"
        ).fetchone()[0]

        in_service = connection.execute(
            "SELECT COUNT(*) FROM assets WHERE LOWER(status) = 'in service'"
        ).fetchone()[0]

        needs_attention = connection.execute(
            """
            SELECT COUNT(*) FROM assets
            WHERE LOWER(status) IN
                ('needs maintenance', 'under maintenance', 'out of service')
            OR LOWER(asset_condition) IN ('poor', 'damaged', 'critical')
            """
        ).fetchone()[0]

        maintenance_cost = connection.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM maintenance_records"
        ).fetchone()[0]

        recent_records = connection.execute(
            """
            SELECT m.maintenance_date, a.asset_code, a.asset_name,
                   COALESCE(l.building, 'Not assigned'),
                   m.description, m.status, m.cost
            FROM maintenance_records AS m
            JOIN assets AS a ON a.asset_id = m.asset_id
            LEFT JOIN locations AS l ON l.location_id = a.location_id
            ORDER BY m.maintenance_id DESC
            LIMIT 8
            """
        ).fetchall()

    return total_assets, in_service, needs_attention, maintenance_cost, recent_records


def show_dashboard(window):
    """Create the BubtOps dashboard."""

    for widget in window.winfo_children():
        widget.destroy()

    window.title("BubtOps | Campus Overview")
    window.geometry("1333x760")
    window.minsize(950, 600)
    window.configure(bg=theme.DASHBOARD_BACKGROUND)
    window.overrideredirect(True)

    # Main container
    layout = tk.Frame(window, bg=theme.DASHBOARD_BACKGROUND)
    layout.pack(fill="both", expand=True)

    # Custom title bar (fixed; does not scroll)
    title_bar = tk.Frame(layout, bg=theme.HEADER_BACKGROUND, height=38)
    title_bar.pack(side="top", fill="x")
    title_bar.pack_propagate(False)

    tk.Label(
        title_bar, text="◆  BubtOps",
        bg=theme.HEADER_BACKGROUND, fg=theme.CYAN,
        font=(theme.FONT_FAMILY, 10, "bold")
    ).pack(side="left", padx=14)

    def minimize_window():
        window.overrideredirect(False)
        window.iconify()

    def restore_borderless(event=None):
        if window.winfo_exists() and window.state() == "normal":
            window.after(100, lambda: window.overrideredirect(True))

    window.bind("<Map>", restore_borderless, add="+")

    def toggle_maximize():
        if getattr(window, "_is_maximized", False):
            window.overrideredirect(False)
            window.state("normal")
            window.geometry("1333x760")
            window.after(100, lambda: window.overrideredirect(True))
            window._is_maximized = False
        else:
            window.overrideredirect(False)
            window.state("zoomed")
            window.after(150, lambda: window.overrideredirect(True))
            window._is_maximized = True

    def make_title_button(text, command, hover_color):
        return tk.Button(
            title_bar, text=text, command=command,
            bg=theme.HEADER_BACKGROUND, fg=theme.TEXT_PRIMARY,
            activebackground=hover_color, activeforeground="#FFFFFF",
            relief="flat", bd=0, width=5, cursor="hand2",
            font=(theme.FONT_FAMILY, 10)
        )

    make_title_button("✕", window.destroy, theme.ERROR).pack(side="right", fill="y")
    make_title_button("□", toggle_maximize, theme.PRIMARY).pack(side="right", fill="y")
    make_title_button("—", minimize_window, theme.PRIMARY).pack(side="right", fill="y")

    def start_drag(event):
        if not getattr(window, "_is_maximized", False):
            window._drag_x = event.x_root - window.winfo_x()
            window._drag_y = event.y_root - window.winfo_y()

    def drag_window(event):
        if not getattr(window, "_is_maximized", False):
            window.geometry(
                f"+{event.x_root - window._drag_x}"
                f"+{event.y_root - window._drag_y}"
            )

    title_bar.bind("<Button-1>", start_drag)
    title_bar.bind("<B1-Motion>", drag_window)

    # Main area: navigation sidebar + dashboard content
    main_area = tk.Frame(layout, bg=theme.DASHBOARD_BACKGROUND)
    main_area.pack(fill="both", expand=True)

    sidebar = tk.Frame(main_area, bg=theme.SIDEBAR_BACKGROUND, width=220)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar, text="WORKSPACE",
        bg=theme.SIDEBAR_BACKGROUND, fg=theme.TEXT_MUTED,
        font=(theme.FONT_FAMILY, 9, "bold")
    ).pack(anchor="w", padx=20, pady=(25, 12))

    def sidebar_item(label, selected=False):
        row_bg = theme.CARD_BACKGROUND if selected else theme.SIDEBAR_BACKGROUND
        fg = theme.CYAN if selected else theme.TEXT_SECONDARY
        item = tk.Frame(sidebar, bg=row_bg, height=42)
        item.pack(fill="x", padx=10, pady=3)
        item.pack_propagate(False)
        tk.Label(
            item, text=label, anchor="w",
            bg=row_bg, fg=fg,
            font=(theme.FONT_FAMILY, 10, "bold" if selected else "normal")
        ).pack(fill="both", expand=True, padx=12)
        if selected:
            tk.Frame(item, bg=theme.CYAN, width=3).pack(side="left", fill="y")
            item.pack_configure(pady=3)

    sidebar_item("▦   Campus Overview", selected=True)
    sidebar_item("▧   Asset Registry")
    sidebar_item("⌖   Locations")
    sidebar_item("⚒   Maintenance")
    sidebar_item("▤   Reports")
    sidebar_item("⚙   Settings")

    # Dashboard content is the only vertically scrolling area.
    content = tk.Frame(main_area, bg=theme.DASHBOARD_BACKGROUND)
    content.pack(side="left", fill="both", expand=True)

    header = tk.Frame(content, bg=theme.HEADER_BACKGROUND)
    header.pack(fill="x")

    header_text = tk.Frame(header, bg=theme.HEADER_BACKGROUND)
    header_text.pack(side="left", padx=28, pady=22)

    tk.Label(
        header_text, text="Campus Overview",
        font=(theme.FONT_FAMILY, 23, "bold"),
        bg=theme.HEADER_BACKGROUND, fg=theme.TEXT_PRIMARY
    ).pack(anchor="w")

    tk.Label(
        header_text, text="Monitor university assets and maintenance",
        font=(theme.FONT_FAMILY, 10),
        bg=theme.HEADER_BACKGROUND, fg=theme.TEXT_SECONDARY
    ).pack(anchor="w", pady=(4, 0))

    tk.Label(
        header, text="● SYSTEM ONLINE",
        font=(theme.FONT_FAMILY, 9, "bold"),
        bg=theme.HEADER_BACKGROUND, fg=theme.SUCCESS
    ).pack(side="right", padx=28)

    # Scrollable canvas area. No visible scrollbar widget is created.
    canvas_area = tk.Frame(content, bg=theme.DASHBOARD_BACKGROUND)
    canvas_area.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        canvas_area, bg=theme.DASHBOARD_BACKGROUND,
        highlightthickness=0, borderwidth=0
    )
    canvas.pack(side="left", fill="both", expand=True)

    body = tk.Frame(canvas, bg=theme.DASHBOARD_BACKGROUND)
    body_window = canvas.create_window((0, 0), window=body, anchor="nw")

    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfigure(body_window, width=canvas.winfo_width())

    body.bind("<Configure>", update_scroll_region)
    canvas.bind("<Configure>", update_scroll_region)

    # Smooth mouse-wheel scrolling. The title bar and sidebar do not scroll.
    target_scroll_y = 0.0
    animation_running = False
    scroll_animation_id = None

    def animate_scroll():
        nonlocal target_scroll_y, animation_running, scroll_animation_id

        bounds = canvas.bbox("all")
        if not bounds:
            animation_running = False
            scroll_animation_id = None
            return

        content_height = max(1, bounds[3] - bounds[1])
        viewport_height = canvas.winfo_height()
        max_scroll = max(0, content_height - viewport_height)
        target_scroll_y = max(0.0, min(target_scroll_y, max_scroll))

        current_y = canvas.yview()[0] * content_height
        difference = target_scroll_y - current_y

        if abs(difference) < 1:
            canvas.yview_moveto(target_scroll_y / content_height)
            animation_running = False
            scroll_animation_id = None
            return

        canvas.yview_moveto((current_y + difference * 0.25) / content_height)
        scroll_animation_id = window.after(10, animate_scroll)

    def scroll_dashboard(event):
        nonlocal target_scroll_y, animation_running

        bounds = canvas.bbox("all")
        if not bounds:
            return "break"

        content_height = max(1, bounds[3] - bounds[1])
        viewport_height = canvas.winfo_height()
        max_scroll = max(0, content_height - viewport_height)

        if not animation_running:
            target_scroll_y = canvas.yview()[0] * content_height

        if event.delta:
            target_scroll_y -= (event.delta / 120.0) * 100

        target_scroll_y = max(0.0, min(target_scroll_y, max_scroll))

        if not animation_running:
            animation_running = True
            animate_scroll()

        return "break"

    def bind_wheel_to_body(widget):
        widget.bind("<MouseWheel>", scroll_dashboard)
        for child in widget.winfo_children():
            bind_wheel_to_body(child)

    # Build widgets first; bind after the body is populated below.
    canvas.bind("<MouseWheel>", scroll_dashboard)

    # Load database statistics
    database_ok = True
    try:
        (
            total_assets, in_service, needs_attention,
            maintenance_cost, recent_records
        ) = get_dashboard_data()
    except sqlite3.Error as error:
        database_ok = False
        total_assets = in_service = needs_attention = 0
        maintenance_cost = 0
        recent_records = []
        messagebox.showerror(
            "Database Error",
            f"Could not read dashboard data:\n\n{error}",
            parent=window
        )

    # Statistic cards
    tk.Label(
        body, text="ASSET SUMMARY",
        font=(theme.FONT_FAMILY, 10, "bold"),
        bg=theme.DASHBOARD_BACKGROUND, fg=theme.TEXT_SECONDARY
    ).pack(anchor="w", padx=24, pady=(22, 12))

    cards = tk.Frame(body, bg=theme.DASHBOARD_BACKGROUND)
    cards.pack(fill="x", padx=18)

    card_data = [
        ("TOTAL ASSETS", f"{total_assets:,}", theme.PRIMARY),
        ("IN SERVICE", f"{in_service:,}", theme.SUCCESS),
        ("NEEDS ATTENTION", f"{needs_attention:,}", theme.WARNING),
        ("MAINTENANCE COST", f"৳{maintenance_cost:,.2f}", theme.PURPLE),
    ]

    for title, value, accent in card_data:
        card = tk.Frame(
            cards, bg=theme.CARD_BACKGROUND,
            highlightbackground=theme.BORDER, highlightthickness=1
        )
        card.pack(side="left", fill="both", expand=True, padx=6)

        tk.Frame(card, bg=accent, height=4).pack(fill="x")
        tk.Label(
            card, text=title, font=(theme.FONT_FAMILY, 9, "bold"),
            bg=theme.CARD_BACKGROUND, fg=theme.TEXT_SECONDARY
        ).pack(anchor="w", padx=14, pady=(16, 7))
        tk.Label(
            card, text=value, font=(theme.FONT_FAMILY, 20, "bold"),
            bg=theme.CARD_BACKGROUND, fg=theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=14, pady=(0, 18))

    # Quick actions
    tk.Label(
        body, text="QUICK ACTIONS",
        font=(theme.FONT_FAMILY, 10, "bold"),
        bg=theme.DASHBOARD_BACKGROUND, fg=theme.TEXT_SECONDARY
    ).pack(anchor="w", padx=24, pady=(26, 12))

    actions = tk.Frame(body, bg=theme.DASHBOARD_BACKGROUND)
    actions.pack(fill="x", padx=24)

    def not_ready(feature):
        messagebox.showinfo(
            feature,
            f"{feature} will be implemented in a later development step.",
            parent=window
        )

    for label, color in [
        ("+  Add Asset", theme.PRIMARY),
        ("+  Log Maintenance", theme.PURPLE),
        ("⌖  Manage Locations", theme.CYAN),
    ]:
        tk.Button(
            actions, text=label,
            command=lambda name=label: not_ready(name),
            bg=color, fg="#FFFFFF",
            activebackground=color, activeforeground="#FFFFFF",
            font=(theme.FONT_FAMILY, 10, "bold"),
            relief="flat", cursor="hand2", padx=14, pady=11
        ).pack(side="left", padx=(0, 10))

    # Recent maintenance table
    tk.Label(
        body, text="RECENT MAINTENANCE",
        font=(theme.FONT_FAMILY, 10, "bold"),
        bg=theme.DASHBOARD_BACKGROUND, fg=theme.TEXT_SECONDARY
    ).pack(anchor="w", padx=24, pady=(28, 12))

    table_frame = tk.Frame(
        body, bg=theme.CARD_BACKGROUND,
        highlightbackground=theme.BORDER, highlightthickness=1
    )
    table_frame.pack(fill="x", padx=24, pady=(0, 24))

    columns = ("date", "code", "asset", "location", "description", "status", "cost")
    headings = {
        "date": "DATE", "code": "ASSET CODE", "asset": "ASSET",
        "location": "BUILDING", "description": "DESCRIPTION",
        "status": "STATUS", "cost": "COST (৳)"
    }
    widths = {
        "date": 95, "code": 105, "asset": 145, "location": 110,
        "description": 190, "status": 115, "cost": 100
    }

    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background=theme.CARD_BACKGROUND,
        fieldbackground=theme.CARD_BACKGROUND,
        foreground=theme.TEXT_PRIMARY,
        rowheight=34, borderwidth=0,
        font=(theme.FONT_FAMILY, 9)
    )
    style.configure(
        "Treeview.Heading",
        background=theme.CARD_BACKGROUND_ALT,
        foreground=theme.CYAN,
        font=(theme.FONT_FAMILY, 9, "bold"),
        relief="flat"
    )
    style.map(
        "Treeview",
        background=[("selected", theme.PRIMARY)],
        foreground=[("selected", "#FFFFFF")]
    )

    table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
    for column in columns:
        table.heading(column, text=headings[column])
        table.column(column, width=widths[column], minwidth=70)
    table.pack(fill="x", expand=True)

    if recent_records:
        for record in recent_records:
            date, code, name, location, description, status, cost = record
            table.insert(
                "", "end",
                values=(date, code, name, location, description, status, f"{cost:,.2f}")
            )
    else:
        table.insert(
            "", "end",
            values=(
                "—", "—", "No records yet", "—",
                "Log maintenance to see records here", "—", "—"
            )
        )

    # Footer
    tk.Label(
        body,
        text=(
            "BubtOps  •  Offline Campus Asset Management  •  "
            + ("Database connected" if database_ok else "Database error")
        ),
        font=(theme.FONT_FAMILY, 9),
        bg=theme.DASHBOARD_BACKGROUND,
        fg=theme.TEXT_MUTED
    ).pack(anchor="w", padx=24, pady=(0, 18))

    # Bind wheel events to all body descendants, including widgets created above.
    bind_wheel_to_body(body)

    # Borderless window resizing
    resize_border = 6
    minimum_width = 950
    minimum_height = 600

    def start_resize(event, direction):
        window._resize_direction = direction
        window._resize_start_x = event.x_root
        window._resize_start_y = event.y_root
        window._resize_start_width = window.winfo_width()
        window._resize_start_height = window.winfo_height()
        window._resize_start_left = window.winfo_x()
        window._resize_start_top = window.winfo_y()

    def perform_resize(event):
        direction = getattr(window, "_resize_direction", None)
        if direction is None:
            return

        dx = event.x_root - window._resize_start_x
        dy = event.y_root - window._resize_start_y
        x = window._resize_start_left
        y = window._resize_start_top
        width = window._resize_start_width
        height = window._resize_start_height

        if "e" in direction:
            width = max(minimum_width, width + dx)
        if "s" in direction:
            height = max(minimum_height, height + dy)
        if "w" in direction:
            new_width = max(minimum_width, width - dx)
            x += width - new_width
            width = new_width
        if "n" in direction:
            new_height = max(minimum_height, height - dy)
            y += height - new_height
            height = new_height

        window.geometry(f"{width}x{height}+{x}+{y}")

    def stop_resize(event=None):
        window._resize_direction = None

    resize_handles = [
        ("n", "sb_v_double_arrow"), ("s", "sb_v_double_arrow"),
        ("e", "sb_h_double_arrow"), ("w", "sb_h_double_arrow"),
        ("nw", "size_nw_se"), ("ne", "size_ne_sw"),
        ("sw", "size_ne_sw"), ("se", "size_nw_se"),
    ]

    for direction, cursor_name in resize_handles:
        handle = tk.Frame(
            window, bg=theme.DASHBOARD_BACKGROUND,
            cursor=cursor_name, bd=0, highlightthickness=0
        )

        if direction == "n":
            handle.place(x=resize_border, y=0, relwidth=1,
                         width=-2 * resize_border, height=resize_border)
        elif direction == "s":
            handle.place(x=resize_border, rely=1, y=-resize_border,
                         relwidth=1, width=-2 * resize_border, height=resize_border)
        elif direction == "e":
            handle.place(relx=1, x=-resize_border, y=resize_border,
                         relheight=1, height=-2 * resize_border, width=resize_border)
        elif direction == "w":
            handle.place(x=0, y=resize_border, relheight=1,
                         height=-2 * resize_border, width=resize_border)
        elif direction == "nw":
            handle.place(x=0, y=0, width=resize_border, height=resize_border)
        elif direction == "ne":
            handle.place(relx=1, x=-resize_border, y=0,
                         width=resize_border, height=resize_border)
        elif direction == "sw":
            handle.place(x=0, rely=1, y=-resize_border,
                         width=resize_border, height=resize_border)
        elif direction == "se":
            handle.place(relx=1, rely=1, x=-resize_border, y=-resize_border,
                         width=resize_border, height=resize_border)

        handle.bind(
            "<ButtonPress-1>",
            lambda event, d=direction: start_resize(event, d)
        )
        handle.bind("<B1-Motion>", perform_resize)
        handle.bind("<ButtonRelease-1>", stop_resize)
  