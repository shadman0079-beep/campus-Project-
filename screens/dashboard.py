
# screens/dashboard.py
# BubtOps - University Asset Maintenance System

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

import theme
from icons import get_icon
from database.db import DATABASE_PATH
from screens.asset_registry import show_asset_registry


# ============================================================
# DATABASE
# ============================================================

def get_dashboard_data():
    with sqlite3.connect(DATABASE_PATH) as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM assets"
        ).fetchone()[0]

        in_service = connection.execute(
            """
            SELECT COUNT(*) FROM assets
            WHERE LOWER(TRIM(status)) = 'in service'
            """
        ).fetchone()[0]

        attention = connection.execute(
            """
            SELECT COUNT(*) FROM assets
            WHERE LOWER(TRIM(status)) IN (
                'needs maintenance', 'under maintenance',
                'out of service'
            )
            OR LOWER(TRIM(asset_condition)) IN (
                'poor', 'damaged', 'critical'
            )
            """
        ).fetchone()[0]

        cost = connection.execute(
            """
            SELECT COALESCE(SUM(cost), 0)
            FROM maintenance_records
            """
        ).fetchone()[0]

        records = connection.execute(
            """
            SELECT
                m.maintenance_date,
                a.asset_code,
                a.asset_name,
                COALESCE(l.building, 'Not assigned'),
                m.description,
                COALESCE(m.status, 'Unknown'),
                COALESCE(m.cost, 0)
            FROM maintenance_records m
            JOIN assets a ON a.asset_id = m.asset_id
            LEFT JOIN locations l ON l.location_id = a.location_id
            ORDER BY m.maintenance_id DESC
            LIMIT 8
            """
        ).fetchall()

    return total, in_service, attention, cost, records


# ============================================================
# REUSABLE HELPERS
# ============================================================

def blend_color(first, second, amount):
    amount = max(0, min(1, amount))
    first = first.lstrip("#")
    second = second.lstrip("#")

    rgb = [
        round(
            int(first[i:i + 2], 16) * (1 - amount)
            + int(second[i:i + 2], 16) * amount
        )
        for i in (0, 2, 4)
    ]

    return "#{:02X}{:02X}{:02X}".format(*rgb)


def safe_money(value):
    try:
        return f"{float(value or 0):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def rounded_shape(canvas, x1, y1, x2, y2, radius, fill, outline=None):
    points = [
        x1 + radius, y1, x2 - radius, y1,
        x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2,
        x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius,
        x1, y1 + radius, x1, y1
    ]

    return canvas.create_polygon(
        points,
        smooth=True,
        splinesteps=24,
        fill=fill,
        outline=outline or fill,
        width=1
    )


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard(window):

    # Cancel animations left by the previous screen.
    for attribute in (
        "_bubtops_sidebar_after",
        "_bubtops_scroll_after"
    ):
        job = getattr(window, attribute, None)
        if job:
            try:
                window.after_cancel(job)
            except tk.TclError:
                pass
        setattr(window, attribute, None)

    for widget in window.winfo_children():
        widget.destroy()

    window._bubtops_icon_images = []

    window.title("BubtOps | Campus Overview")
    window.configure(bg=theme.DASHBOARD_BACKGROUND)
    window.minsize(950, 600)

    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()

    width = min(1333, max(950, screen_w - 60))
    height = min(760, max(600, screen_h - 100))
    x = max(0, (screen_w - width) // 2)
    y = max(0, (screen_h - height) // 2)

    restore_geometry = f"{width}x{height}+{x}+{y}"

    window._bubtops_restore_geometry = restore_geometry
    window._is_maximized = False
    window.geometry(restore_geometry)
    window.overrideredirect(True)

    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    layout = tk.Frame(window, bg=theme.DASHBOARD_BACKGROUND)
    layout.pack(fill="both", expand=True)

    title_bar = tk.Frame(
        layout,
        bg=theme.HEADER_BACKGROUND,
        height=38
    )
    title_bar.pack(fill="x")
    title_bar.pack_propagate(False)

    tk.Label(
        title_bar,
        text="◆  BubtOps",
        bg=theme.HEADER_BACKGROUND,
        fg=theme.CYAN,
        font=(theme.FONT_FAMILY, 10, "bold")
    ).pack(side="left", padx=14)

    def restore_borderless(event=None):
        if (
            window.winfo_exists()
            and window.state() == "normal"
            and not window._is_maximized
        ):
            window.after(
                100,
                lambda: window.overrideredirect(True)
                if window.winfo_exists() else None
            )

    old_binding = getattr(window, "_bubtops_map_binding", None)
    if old_binding:
        try:
            window.unbind("<Map>", old_binding)
        except tk.TclError:
            pass

    window._bubtops_map_binding = window.bind(
        "<Map>", restore_borderless, add="+"
    )

    def minimize_window():
        window.overrideredirect(False)
        window.iconify()

    def toggle_maximize():
        if window._is_maximized:
            window.overrideredirect(False)
            window.state("normal")
            window.geometry(window._bubtops_restore_geometry)
            window._is_maximized = False
        else:
            window._bubtops_restore_geometry = (
                f"{window.winfo_width()}x{window.winfo_height()}"
                f"+{window.winfo_x()}+{window.winfo_y()}"
            )
            window.overrideredirect(False)
            window.state("zoomed")
            window._is_maximized = True

        window.after(
            150,
            lambda: window.overrideredirect(True)
            if window.winfo_exists() else None
        )

    def title_button(text, command, hover):
        button = tk.Button(
            title_bar,
            text=text,
            command=command,
            bg=theme.HEADER_BACKGROUND,
            fg=theme.TEXT_PRIMARY,
            activebackground=hover,
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            width=5,
            cursor="hand2",
            font=(theme.FONT_FAMILY, 10),
            highlightthickness=0
        )
        button.bind("<Enter>", lambda e: button.configure(bg=hover))
        button.bind(
            "<Leave>",
            lambda e: button.configure(bg=theme.HEADER_BACKGROUND)
        )
        return button

    title_button("✕", window.destroy, theme.ERROR).pack(
        side="right", fill="y"
    )
    title_button("□", toggle_maximize, theme.PRIMARY).pack(
        side="right", fill="y"
    )
    title_button("—", minimize_window, theme.PRIMARY).pack(
        side="right", fill="y"
    )

    def start_drag(event):
        if not window._is_maximized:
            window._drag_x = event.x_root - window.winfo_x()
            window._drag_y = event.y_root - window.winfo_y()

    def drag_window(event):
        if not window._is_maximized:
            window.geometry(
                f"+{event.x_root - window._drag_x}"
                f"+{event.y_root - window._drag_y}"
            )

    def bind_drag(widget):
        if isinstance(widget, tk.Button):
            return
        widget.bind("<Button-1>", start_drag)
        widget.bind("<B1-Motion>", drag_window)
        for child in widget.winfo_children():
            bind_drag(child)

    bind_drag(title_bar)

    # --------------------------------------------------------
    # MAIN AREA AND SIDEBAR
    # --------------------------------------------------------

    main_area = tk.Frame(
        layout,
        bg=theme.DASHBOARD_BACKGROUND
    )
    main_area.pack(fill="both", expand=True)

    # Increased sidebar width.
    SIDEBAR_WIDTH = 100

    sidebar = tk.Frame(
        main_area,
        bg=theme.SIDEBAR_BACKGROUND,
        width=SIDEBAR_WIDTH
    )
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Frame(
        sidebar,
        bg=theme.BORDER,
        width=1
    ).pack(side="right", fill="y")

    brand_image = get_icon(
        "boxes", size=25, color=theme.CYAN
    )
    brand = tk.Label(
        sidebar,
        image=brand_image,
        bg=theme.SIDEBAR_BACKGROUND
    )
    brand.image = brand_image
    brand.pack(pady=(21, 22))
    window._bubtops_icon_images.append(brand_image)

    nav_container = tk.Frame(
        sidebar,
        bg=theme.SIDEBAR_BACKGROUND
    )
    nav_container.pack(fill="x")

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    def open_asset_registry():
        job = getattr(window, "_bubtops_scroll_after", None)
        if job:
            try:
                window.after_cancel(job)
            except tk.TclError:
                pass
        show_asset_registry(window)

    def not_ready(feature):
        messagebox.showinfo(
            feature,
            f"{feature} will be implemented in a later development step.",
            parent=window
        )

    nav_items = []
    nav_animation = {
        "progress": 0.0,
        "target": 0.0,
        "active": None,
        "job": None
    }

    def cancel_nav_animation():
        job = nav_animation["job"]
        if job:
            try:
                window.after_cancel(job)
            except tk.TclError:
                pass
        nav_animation["job"] = None
        window._bubtops_sidebar_after = None

    def animate_nav():
        state = nav_animation
        difference = state["target"] - state["progress"]

        if abs(difference) < 0.025:
            state["progress"] = state["target"]
        else:
            state["progress"] += difference * 0.38

        progress = state["progress"]
        active = state["active"]

        for item in nav_items:
            selected = item["selected"]
            hovered = item is active

            if hovered:
                icon_x = 8 - round(3 * progress)
                label_color = blend_color(
                    theme.SIDEBAR_BACKGROUND,
                    theme.TEXT_PRIMARY,
                    progress
                )
            else:
                icon_x = 8
                label_color = theme.SIDEBAR_BACKGROUND

            item["icon"].place(
                x=icon_x,
                rely=0.5,
                anchor="w"
            )
            item["label_widget"].configure(fg=label_color)

            if selected:
                item["row"].configure(bg=theme.CARD_BACKGROUND)
                item["icon"].configure(bg=theme.CARD_BACKGROUND)
                item["label_widget"].configure(
                    bg=theme.CARD_BACKGROUND
                )
            elif hovered:
                item["row"].configure(
                    bg=theme.CARD_BACKGROUND_ALT
                )
                item["icon"].configure(
                    bg=theme.CARD_BACKGROUND_ALT
                )
                item["label_widget"].configure(
                    bg=theme.CARD_BACKGROUND_ALT
                )
            else:
                item["row"].configure(
                    bg=theme.SIDEBAR_BACKGROUND
                )
                item["icon"].configure(
                    bg=theme.SIDEBAR_BACKGROUND
                )
                item["label_widget"].configure(
                    bg=theme.SIDEBAR_BACKGROUND
                )

        if progress == 0 and state["target"] == 0:
            state["job"] = None
            window._bubtops_sidebar_after = None
            return

        if progress == state["target"]:
            state["job"] = None
            window._bubtops_sidebar_after = None
            return

        state["job"] = window.after(12, animate_nav)
        window._bubtops_sidebar_after = state["job"]

    def start_nav_animation():
        cancel_nav_animation()
        animate_nav()

    def nav_enter(item):
        nav_animation["active"] = item
        nav_animation["target"] = 1.0
        start_nav_animation()

    def nav_leave(item):
        def check_pointer():
            try:
                pointer = window.winfo_containing(
                    window.winfo_pointerx(),
                    window.winfo_pointery()
                )
                while pointer:
                    if pointer == item["row"]:
                        return
                    pointer = pointer.master
            except tk.TclError:
                pass

            if nav_animation["active"] is item:
                nav_animation["active"] = None
                nav_animation["target"] = 0.0
                start_nav_animation()

        window.after(45, check_pointer)

    def create_nav_item(icon_name, label, short_label,
                        selected=False, command=None):

        background = (
            theme.CARD_BACKGROUND
            if selected else theme.SIDEBAR_BACKGROUND
        )

        # Wider navigation button to prevent icon/label overlap.
        row = tk.Frame(
            nav_container,
            bg=background,
            width=86,
            height=46,
            cursor="hand2"
        )
        row.pack(padx=6, pady=4)
        row.pack_propagate(False)

        icon_image = get_icon(
            icon_name,
            size=19,
            color=theme.CYAN if selected else theme.TEXT_SECONDARY
        )

        icon = tk.Label(
            row,
            image=icon_image,
            bg=background,
            bd=0,
            cursor="hand2"
        )
        icon.image = icon_image
        icon.place(
            x=8,
            rely=0.5,
            anchor="w"
        )
        window._bubtops_icon_images.append(icon_image)

        label_widget = tk.Label(
            row,
            text=short_label,
            bg=background,
            fg=background,
            font=(theme.FONT_FAMILY, 7, "bold"),
            anchor="w",
            bd=0,
            cursor="hand2"
        )
        label_widget.place(
            x=32,
            rely=0.5,
            anchor="w",
            width=49
        )

        item = {
            "row": row,
            "icon": icon,
            "label_widget": label_widget,
            "label": label,
            "selected": selected
        }
        nav_items.append(item)

        for widget in (row, icon, label_widget):
            widget.bind(
                "<Enter>",
                lambda e, current=item: nav_enter(current)
            )
            widget.bind(
                "<Leave>",
                lambda e, current=item: nav_leave(current)
            )

            if command:
                widget.bind(
                    "<Button-1>",
                    lambda e, action=command: action()
                )

        return row

    create_nav_item(
        "layout-dashboard", "Campus Overview", "HOME",
        selected=True
    )
    create_nav_item(
        "package", "Asset Registry", "ASSETS",
        command=open_asset_registry
    )
    create_nav_item(
        "map-pin", "Locations", "MAP",
        command=lambda: not_ready("Locations")
    )
    create_nav_item(
        "wrench", "Maintenance", "SERVICE",
        command=lambda: not_ready("Maintenance")
    )
    create_nav_item(
        "chart-column", "Reports", "REPORTS",
        command=lambda: not_ready("Reports")
    )
    create_nav_item(
        "settings", "Settings", "SET",
        command=lambda: not_ready("Settings")
    )

    # --------------------------------------------------------
    # CONTENT HOST
    # --------------------------------------------------------

    content = tk.Frame(
        main_area,
        bg=theme.DASHBOARD_BACKGROUND
    )
    content.pack(side="left", fill="both", expand=True)
    window._bubtops_content_host = content

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        content,
        bg=theme.HEADER_BACKGROUND
    )
    header.pack(fill="x")

    header_text = tk.Frame(
        header,
        bg=theme.HEADER_BACKGROUND
    )
    header_text.pack(side="left", padx=28, pady=22)

    tk.Label(
        header_text,
        text="Campus Overview",
        font=(theme.FONT_FAMILY, 23, "bold"),
        bg=theme.HEADER_BACKGROUND,
        fg=theme.TEXT_PRIMARY
    ).pack(anchor="w")

    tk.Label(
        header_text,
        text="Monitor university assets and maintenance",
        font=(theme.FONT_FAMILY, 10),
        bg=theme.HEADER_BACKGROUND,
        fg=theme.TEXT_SECONDARY
    ).pack(anchor="w", pady=(4, 0))

    tk.Label(
        header,
        text="● SYSTEM ONLINE",
        font=(theme.FONT_FAMILY, 9, "bold"),
        bg=theme.HEADER_BACKGROUND,
        fg=theme.SUCCESS
    ).pack(side="right", padx=24)

    # --------------------------------------------------------
    # THEME SELECTOR
    # --------------------------------------------------------

    def change_theme(name):
        if name not in theme.THEMES:
            return
        theme.apply_theme(name)
        theme.save_theme(name)
        window.after_idle(lambda: show_dashboard(window))

    theme_menu = tk.Menu(
        header,
        tearoff=0,
        bg=theme.CARD_BACKGROUND,
        fg=theme.TEXT_PRIMARY,
        activebackground=theme.PRIMARY,
        activeforeground="#FFFFFF",
        borderwidth=0,
        relief="flat",
        font=(theme.FONT_FAMILY, 10)
    )

    for name in theme.THEMES:
        theme_menu.add_command(
            label=f"   ◈   {name}",
            command=lambda selected=name: change_theme(selected)
        )

    def open_theme_menu():
        theme_selector.update_idletasks()
        try:
            theme_menu.tk_popup(
                theme_selector.winfo_rootx(),
                theme_selector.winfo_rooty()
                + theme_selector.winfo_height()
            )
        finally:
            theme_menu.grab_release()

    theme_selector = tk.Button(
        header,
        text=f"◈  {theme.ACTIVE_THEME_NAME}   ▾",
        command=open_theme_menu,
        bg=theme.CARD_BACKGROUND_ALT,
        fg=theme.TEXT_PRIMARY,
        activebackground=theme.CARD_BACKGROUND,
        activeforeground=theme.CYAN,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=theme.BORDER,
        cursor="hand2",
        font=(theme.FONT_FAMILY, 9, "bold"),
        padx=14,
        pady=9
    )
    theme_selector.pack(side="right", padx=(0, 18), pady=10)
    theme_selector.bind(
        "<Enter>",
        lambda e: theme_selector.configure(
            bg=theme.CARD_BACKGROUND
        )
    )
    theme_selector.bind(
        "<Leave>",
        lambda e: theme_selector.configure(
            bg=theme.CARD_BACKGROUND_ALT
        )
    )

    # --------------------------------------------------------
    # SCROLLABLE BODY
    # --------------------------------------------------------

    canvas_area = tk.Frame(
        content,
        bg=theme.DASHBOARD_BACKGROUND
    )
    canvas_area.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        canvas_area,
        bg=theme.DASHBOARD_BACKGROUND,
        highlightthickness=0,
        borderwidth=0
    )
    canvas.pack(fill="both", expand=True)

    body = tk.Frame(
        canvas,
        bg=theme.DASHBOARD_BACKGROUND
    )
    body_window = canvas.create_window(
        (0, 0), window=body, anchor="nw"
    )

    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfigure(
            body_window,
            width=canvas.winfo_width()
        )

    body.bind("<Configure>", update_scroll_region)
    canvas.bind("<Configure>", update_scroll_region)

    scroll = {"target": 0.0, "running": False, "job": None}

    def animate_scroll():
        if not canvas.winfo_exists():
            scroll["running"] = False
            scroll["job"] = None
            window._bubtops_scroll_after = None
            return

        bounds = canvas.bbox("all")
        if not bounds:
            scroll["running"] = False
            scroll["job"] = None
            window._bubtops_scroll_after = None
            return

        content_height = max(1, bounds[3] - bounds[1])
        viewport = canvas.winfo_height()
        maximum = max(0, content_height - viewport)

        scroll["target"] = max(
            0, min(scroll["target"], maximum)
        )

        current = canvas.yview()[0] * content_height
        difference = scroll["target"] - current

        if abs(difference) < 1:
            canvas.yview_moveto(scroll["target"] / content_height)
            scroll["running"] = False
            scroll["job"] = None
            window._bubtops_scroll_after = None
            return

        canvas.yview_moveto(
            (current + difference * 0.24) / content_height
        )

        scroll["job"] = window.after(12, animate_scroll)
        window._bubtops_scroll_after = scroll["job"]

    def scroll_dashboard(event):
        bounds = canvas.bbox("all")
        if not bounds:
            return "break"

        content_height = max(1, bounds[3] - bounds[1])
        maximum = max(0, content_height - canvas.winfo_height())

        if not scroll["running"]:
            scroll["target"] = canvas.yview()[0] * content_height

        if event.delta:
            scroll["target"] -= event.delta / 120 * 100
        elif getattr(event, "num", None) == 4:
            scroll["target"] -= 100
        elif getattr(event, "num", None) == 5:
            scroll["target"] += 100

        scroll["target"] = max(
            0, min(scroll["target"], maximum)
        )

        if not scroll["running"]:
            scroll["running"] = True
            animate_scroll()

        return "break"

    def bind_mousewheel(widget):
        widget.bind("<MouseWheel>", scroll_dashboard)
        widget.bind("<Button-4>", scroll_dashboard)
        widget.bind("<Button-5>", scroll_dashboard)

        for child in widget.winfo_children():
            bind_mousewheel(child)

    canvas.bind("<MouseWheel>", scroll_dashboard)
    canvas.bind("<Button-4>", scroll_dashboard)
    canvas.bind("<Button-5>", scroll_dashboard)

    # --------------------------------------------------------
    # DATABASE DATA
    # --------------------------------------------------------

    database_ok = True

    try:
        (
            total_assets,
            in_service,
            needs_attention,
            maintenance_cost,
            recent_records
        ) = get_dashboard_data()

    except (sqlite3.Error, OSError) as error:
        database_ok = False
        total_assets = in_service = needs_attention = 0
        maintenance_cost = 0
        recent_records = []

        messagebox.showerror(
            "Database Error",
            f"Could not read dashboard data:\n\n{error}",
            parent=window
        )

    # --------------------------------------------------------
    # SECTION LABEL HELPER
    # --------------------------------------------------------

    def section_label(text, top=24):
        tk.Label(
            body,
            text=text,
            font=(theme.FONT_FAMILY, 10, "bold"),
            bg=theme.DASHBOARD_BACKGROUND,
            fg=theme.TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=24,
            pady=(top, 12)
        )

    # --------------------------------------------------------
    # ASSET SUMMARY CARDS
    # --------------------------------------------------------

    section_label("ASSET SUMMARY", 22)

    cards = tk.Frame(
        body,
        bg=theme.DASHBOARD_BACKGROUND
    )
    cards.pack(fill="x", padx=18)

    card_data = [
        ("TOTAL ASSETS", f"{total_assets:,}", theme.PRIMARY),
        ("IN SERVICE", f"{in_service:,}", theme.SUCCESS),
        ("NEEDS ATTENTION", f"{needs_attention:,}", theme.WARNING),
        ("MAINTENANCE COST", f"৳{safe_money(maintenance_cost)}", theme.PURPLE)
    ]

    def create_summary_card(parent, title, value, accent):
        card = tk.Canvas(
            parent,
            height=145,
            bg=theme.DASHBOARD_BACKGROUND,
            highlightthickness=0,
            bd=0
        )
        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        hover = {"active": False}

        def draw(event=None):
            card.delete("all")
            width = card.winfo_width()
            height = card.winfo_height()

            if width < 10 or height < 10:
                return

            background = (
                theme.CARD_BACKGROUND_ALT
                if hover["active"]
                else theme.CARD_BACKGROUND
            )

            rounded_shape(
                card, 2, 2, width - 3, height - 3,
                18, background, theme.BORDER
            )

            card.create_line(
                22, 27, 54, 27,
                fill=accent,
                width=3,
                capstyle="round"
            )

            card.create_text(
                22, 48,
                text=title,
                anchor="w",
                fill=theme.TEXT_SECONDARY,
                font=(theme.FONT_FAMILY, 9, "bold")
            )

            card.create_text(
                22, 83,
                text=value,
                anchor="w",
                fill=theme.TEXT_PRIMARY,
                font=(theme.FONT_FAMILY, 19, "bold")
            )

        def enter(event):
            hover["active"] = True
            draw()

        def leave(event):
            hover["active"] = False
            draw()

        card.bind("<Configure>", draw)
        card.bind("<Enter>", enter)
        card.bind("<Leave>", leave)
        return card

    for title, value, accent in card_data:
        create_summary_card(cards, title, value, accent)

    # --------------------------------------------------------
    # QUICK ACTIONS
    # --------------------------------------------------------

    section_label("QUICK ACTIONS", 26)

    actions = tk.Frame(
        body,
        bg=theme.DASHBOARD_BACKGROUND
    )
    actions.pack(fill="x", padx=24)

    def create_action_button(label, color, command):
        hover = blend_color(color, "#FFFFFF", 0.13)

        button = tk.Button(
            actions,
            text=label,
            command=command,
            bg=color,
            fg="#FFFFFF",
            activebackground=hover,
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(theme.FONT_FAMILY, 10, "bold"),
            padx=14,
            pady=10,
            highlightthickness=0
        )

        button.bind(
            "<Enter>",
            lambda e: button.configure(bg=hover)
        )
        button.bind(
            "<Leave>",
            lambda e: button.configure(bg=color)
        )
        button.pack(side="left", padx=(0, 10))

    create_action_button(
        "+  Add Asset", theme.PRIMARY, open_asset_registry
    )
    create_action_button(
        "+  Log Maintenance", theme.PURPLE,
        lambda: not_ready("Log Maintenance")
    )
    create_action_button(
        "⌖  Manage Locations", theme.CYAN,
        lambda: not_ready("Manage Locations")
    )

    # --------------------------------------------------------
    # RECENT MAINTENANCE
    # --------------------------------------------------------

    section_label("RECENT MAINTENANCE", 28)

    table_frame = tk.Frame(
        body,
        bg=theme.CARD_BACKGROUND,
        highlightbackground=theme.BORDER,
        highlightthickness=1,
        bd=0
    )
    table_frame.pack(
        fill="x",
        padx=24,
        pady=(0, 24)
    )

    columns = (
        "date", "code", "asset", "location",
        "description", "status", "cost"
    )

    headings = {
        "date": "DATE",
        "code": "ASSET CODE",
        "asset": "ASSET",
        "location": "BUILDING",
        "description": "DESCRIPTION",
        "status": "STATUS",
        "cost": "COST (৳)"
    }

    widths = {
        "date": 95,
        "code": 105,
        "asset": 145,
        "location": 110,
        "description": 190,
        "status": 115,
        "cost": 100
    }

    style = ttk.Style(window)
    style.theme_use("clam")

    style.configure(
        "BubtOps.Treeview",
        background=theme.CARD_BACKGROUND,
        fieldbackground=theme.CARD_BACKGROUND,
        foreground=theme.TEXT_PRIMARY,
        rowheight=36,
        borderwidth=0,
        font=(theme.FONT_FAMILY, 9)
    )

    style.configure(
        "BubtOps.Treeview.Heading",
        background=theme.CARD_BACKGROUND_ALT,
        foreground=theme.CYAN,
        font=(theme.FONT_FAMILY, 9, "bold"),
        relief="flat",
        padding=(8, 10)
    )

    style.map(
        "BubtOps.Treeview",
        background=[("selected", theme.PRIMARY)],
        foreground=[("selected", "#FFFFFF")]
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        height=8,
        style="BubtOps.Treeview",
        selectmode="browse"
    )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=table.xview
    )
    table.configure(xscrollcommand=scrollbar.set)

    for column in columns:
        table.heading(column, text=headings[column])
        table.column(
            column,
            width=widths[column],
            minwidth=70,
            stretch=False
        )

    table.pack(fill="x", expand=True)
    scrollbar.pack(fill="x")

    if recent_records:
        for record in recent_records:
            date, code, name, location, description, status, cost = record

            table.insert(
                "",
                "end",
                values=(
                    date or "—",
                    code or "—",
                    name or "—",
                    location or "Not assigned",
                    description or "—",
                    status or "Unknown",
                    safe_money(cost)
                )
            )
    else:
        table.insert(
            "",
            "end",
            values=(
                "—", "—", "No records yet", "—",
                "Log maintenance to see records here",
                "—", "—"
            )
        )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    footer = (
        "BubtOps  •  Offline Campus Asset Management  •  "
        + ("Database connected" if database_ok else "Database error")
    )

    tk.Label(
        body,
        text=footer,
        font=(theme.FONT_FAMILY, 9),
        bg=theme.DASHBOARD_BACKGROUND,
        fg=theme.TEXT_MUTED
    ).pack(anchor="w", padx=24, pady=(0, 18))

    bind_mousewheel(body)

    # --------------------------------------------------------
    # BORDERLESS WINDOW RESIZING
    # --------------------------------------------------------

    border = 6
    min_width, min_height = 950, 600

    def start_resize(event, direction):
        if window._is_maximized:
            return

        window._resize_direction = direction
        window._resize_start_x = event.x_root
        window._resize_start_y = event.y_root
        window._resize_start_width = window.winfo_width()
        window._resize_start_height = window.winfo_height()
        window._resize_start_left = window.winfo_x()
        window._resize_start_top = window.winfo_y()

    def perform_resize(event):
        direction = getattr(window, "_resize_direction", None)
        if direction is None or window._is_maximized:
            return

        dx = event.x_root - window._resize_start_x
        dy = event.y_root - window._resize_start_y

        x = window._resize_start_left
        y = window._resize_start_top
        width = window._resize_start_width
        height = window._resize_start_height

        if "e" in direction:
            width = max(min_width, width + dx)
        if "s" in direction:
            height = max(min_height, height + dy)
        if "w" in direction:
            new_width = max(min_width, width - dx)
            x += width - new_width
            width = new_width
        if "n" in direction:
            new_height = max(min_height, height - dy)
            y += height - new_height
            height = new_height

        window.geometry(f"{width}x{height}+{x}+{y}")

    def stop_resize(event=None):
        window._resize_direction = None

    handles = [
        ("n", "sb_v_double_arrow"),
        ("s", "sb_v_double_arrow"),
        ("e", "sb_h_double_arrow"),
        ("w", "sb_h_double_arrow"),
        ("nw", "size_nw_se"),
        ("ne", "size_ne_sw"),
        ("sw", "size_ne_sw"),
        ("se", "size_nw_se")
    ]

    window._bubtops_resize_handles = []

    for direction, cursor in handles:
        handle = tk.Frame(
            window,
            bg=theme.DASHBOARD_BACKGROUND,
            cursor=cursor,
            bd=0,
            highlightthickness=0
        )

        if direction == "n":
            handle.place(
                x=border, y=0, relwidth=1,
                width=-2 * border, height=border
            )
        elif direction == "s":
            handle.place(
                x=border, rely=1, y=-border,
                relwidth=1, width=-2 * border,
                height=border
            )
        elif direction == "e":
            handle.place(
                relx=1, x=-border, y=border,
                relheight=1, height=-2 * border,
                width=border
            )
        elif direction == "w":
            handle.place(
                x=0, y=border, relheight=1,
                height=-2 * border, width=border
            )
        elif direction == "nw":
            handle.place(x=0, y=0, width=border, height=border)
        elif direction == "ne":
            handle.place(
                relx=1, x=-border, y=0,
                width=border, height=border
            )
        elif direction == "sw":
            handle.place(
                x=0, rely=1, y=-border,
                width=border, height=border
            )
        elif direction == "se":
            handle.place(
                relx=1, rely=1, x=-border, y=-border,
                width=border, height=border
            )

        handle.bind(
            "<ButtonPress-1>",
            lambda e, d=direction: start_resize(e, d)
        )
        handle.bind("<B1-Motion>", perform_resize)
        handle.bind("<ButtonRelease-1>", stop_resize)

        window._bubtops_resize_handles.append(handle)
        handle.lift()
