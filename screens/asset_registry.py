
# screens/asset_registry.py
# BubtOps - Asset Registry
# Same-window navigation with SQLite asset management.

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import theme 
from database.db import DATABASE_PATH


CONDITIONS = ("Good", "Fair", "Poor", "Damaged", "Critical")

STATUSES = (
    "In Service",
    "Needs Maintenance",
    "Under Maintenance",
    "Out of Service",
)

FIELD_BG = "#1B2F4B"
FIELD_BORDER = "#426080"
FIELD_FOCUS = "#2B82FF"
BUTTON_TEXT = "#FFFFFF"


def show_asset_registry(parent):
    """Display Asset Registry inside BubtOps's existing window."""
        # Get colors from the currently selected application theme.
    FIELD_BG = theme.CARD_BACKGROUND_ALT
    FIELD_BORDER = theme.BORDER
    FIELD_FOCUS = theme.PRIMARY
    BUTTON_TEXT = "#FFFFFF"

    # Reuse the content area created by dashboard.py.
    host = getattr(parent, "_bubtops_content_host", None)

    if host is None or not host.winfo_exists():
        messagebox.showerror(
            "Navigation Error",
            "The BubtOps content area was not found.\n\n"
            "Please restart the application.",
            parent=parent,
        )
        return

    # Clear the previous screen without destroying the main window.
    for widget in host.winfo_children():
        widget.destroy()

    host.configure(bg=theme .DASHBOARD_BACKGROUND)

    selected_id = {"value": None}
    location_map = {}

    # ---------------------------------------------------------
    # DATABASE CONNECTION
    # ---------------------------------------------------------

    def connect():
        connection = sqlite3.connect(DATABASE_PATH)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    # ---------------------------------------------------------
    # WIDGET STYLES
    # ---------------------------------------------------------

    style = ttk.Style(parent)

    style.configure(
        "AssetRegistry.TCombobox",
        fieldbackground=FIELD_BG,
        background=FIELD_BG,
        foreground=theme.TEXT_PRIMARY,
        arrowcolor=theme.CYAN,
        bordercolor=FIELD_BORDER,
        lightcolor=FIELD_BORDER,
        darkcolor=FIELD_BORDER,
        padding=7,
    )

    style.map(
        "AssetRegistry.TCombobox",
        fieldbackground=[("readonly", FIELD_BG)],
        foreground=[("readonly", theme.TEXT_PRIMARY)],
        selectbackground=[("readonly", FIELD_BG)],
        selectforeground=[("readonly", theme.TEXT_PRIMARY)],
        bordercolor=[
            ("focus", FIELD_FOCUS),
            ("!focus", FIELD_BORDER),
        ],
    )

    style.configure(
        "AssetRegistry.Treeview",
        background=theme.CARD_BACKGROUND,
        fieldbackground=theme.CARD_BACKGROUND,
        foreground=theme.TEXT_PRIMARY,
        rowheight=32,
        borderwidth=0,
        font=(theme.FONT_FAMILY, 9),
    )

    style.configure(
        "AssetRegistry.Treeview.Heading",
        background=theme.CARD_BACKGROUND_ALT,
        foreground=theme.CYAN,
        font=(theme.FONT_FAMILY, 9, "bold"),
        relief="flat",
        padding=7,
    )

    style.map(
        "AssetRegistry.Treeview",
        background=[("selected", theme.PRIMARY)],
        foreground=[("selected", "#FFFFFF")],
    )

    # ---------------------------------------------------------
    # REUSABLE UI HELPERS
    # ---------------------------------------------------------

    def make_label(
        container,
        text,
        color=None,
        size=9,
        bold=False,
    ):
        return tk.Label(
            container,
            text=text,
            bg=container.cget("bg"),
            fg=color or theme.TEXT_SECONDARY,
            font=(
                theme.FONT_FAMILY,
                size,
                "bold" if bold else "normal",
            ),
            anchor="w",
        )

    def make_entry(container, variable=None):
        """Create a text entry with a visible border."""

        border = tk.Frame(
            container,
            bg=FIELD_BORDER,
            padx=1,
            pady=1,
        )

        entry = tk.Entry(
            border,
            textvariable=variable,
            bg=FIELD_BG,
            fg=theme.TEXT_PRIMARY,
            insertbackground=theme.TEXT_PRIMARY,
            selectbackground=theme.PRIMARY,
            selectforeground="#FFFFFF",
            relief="flat",
            bd=0,
            font=(theme.FONT_FAMILY, 10),
        )

        entry.pack(
            fill="both",
            expand=True,
            padx=7,
            ipady=5,
        )

        entry.bind(
            "<FocusIn>",
            lambda event: border.configure(bg=FIELD_FOCUS),
        )

        entry.bind(
            "<FocusOut>",
            lambda event: border.configure(bg=FIELD_BORDER),
        )

        return border, entry

    def make_button(container, label, command, color):
        return tk.Button(
            container,
            text=label,
            command=command,
            bg=color,
            fg=BUTTON_TEXT,
            activebackground=color,
            activeforeground=BUTTON_TEXT,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(theme.FONT_FAMILY, 9, "bold"),
            padx=11,
            pady=8,
        )

    def show_database_error(error):
        messagebox.showerror(
            "Database Error",
            str(error),
            parent=parent,
        )

    # ---------------------------------------------------------
    # PAGE HEADER AND BACK BUTTON
    # ---------------------------------------------------------

    header = tk.Frame(
        host,
        bg=theme.HEADER_BACKGROUND,
    )
    header.pack(fill="x")

    header_text = tk.Frame(
        header,
        bg=theme.HEADER_BACKGROUND,
    )
    header_text.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(22, 5),
        pady=16,
    )

    tk.Label(
        header_text,
        text="Asset Registry",
        bg=theme.HEADER_BACKGROUND,
        fg=theme.TEXT_PRIMARY,
        font=(theme.FONT_FAMILY, 21, "bold"),
    ).pack(anchor="w")

    tk.Label(
        header_text,
        text="Register, search, update and manage campus assets.",
        bg=theme.HEADER_BACKGROUND,
        fg=theme.TEXT_SECONDARY,
        font=(theme.FONT_FAMILY, 9),
        wraplength=360,
        justify="left",
    ).pack(anchor="w", pady=(4, 0))

    def go_back():
        # Import here to avoid a circular import between screens.
        from screens.dashboard import show_dashboard

        show_dashboard(parent)

    back_button = tk.Button(
        header,
        text="←  Back to Dashboard",
        command=go_back,
        bg=theme.PRIMARY,
        fg="#FFFFFF",
        activebackground=theme.NAVY,
        activeforeground="#FFFFFF",
        relief="flat",
        bd=0,
        cursor="hand2",
        font=(theme.FONT_FAMILY, 9, "bold"),
        padx=10,
        pady=9,
    )
    back_button.pack(
        side="right",
        padx=16,
        pady=18,
    )

    # ---------------------------------------------------------
    # SCROLLABLE PAGE BODY
    # ---------------------------------------------------------

    body_container = tk.Frame(
        host,
        bg=theme.DASHBOARD_BACKGROUND,
    )
    body_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        body_container,
        bg=theme.DASHBOARD_BACKGROUND,
        highlightthickness=0,
        borderwidth=0,
    )
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        body_container,
        orient="vertical",
        command=canvas.yview,
    )
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    body = tk.Frame(
        canvas,
        bg=theme.DASHBOARD_BACKGROUND,
    )

    body_window = canvas.create_window(
        (0, 0),
        window=body,
        anchor="nw",
    )

    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfigure(
            body_window,
            width=canvas.winfo_width(),
        )

    body.bind("<Configure>", update_scroll_region)
    canvas.bind("<Configure>", update_scroll_region)

    def scroll_page(event):
        if event.delta:
            canvas.yview_scroll(
                int(-event.delta / 120),
                "units",
            )
        return "break"

    def bind_mousewheel(widget):
        widget.bind("<MouseWheel>", scroll_page)

        for child in widget.winfo_children():
            bind_mousewheel(child)

    canvas.bind("<MouseWheel>", scroll_page)

    # ---------------------------------------------------------
    # ASSET FORM PANEL
    # ---------------------------------------------------------

    form = tk.Frame(
        body,
        bg=theme.CARD_BACKGROUND,
        highlightbackground=theme.BORDER,
        highlightthickness=1,
    )
    form.pack(
        fill="x",
        padx=18,
        pady=(18, 14),
    )

    tk.Label(
        form,
        text="ASSET DETAILS",
        bg=theme.CARD_BACKGROUND,
        fg=theme.CYAN,
        font=(theme.FONT_FAMILY, 10, "bold"),
    ).grid(
        row=0,
        column=0,
        columnspan=4,
        sticky="w",
        padx=14,
        pady=(13, 10),
    )

    fields = {}

    field_info = [
        ("Asset Code *", "asset_code"),
        ("Asset Name *", "asset_name"),
        ("Category *", "category"),
        ("Purchase Date", "purchase_date"),
    ]

    for index, (label_text, key) in enumerate(field_info):
        row_number = 1 + index // 2
        column_number = (index % 2) * 2

        make_label(
            form,
            label_text,
            size=9,
            bold=True,
        ).grid(
            row=row_number,
            column=column_number,
            sticky="w",
            padx=(14, 8),
            pady=(4, 3),
        )

        border, entry = make_entry(form)

        border.grid(
            row=row_number,
            column=column_number + 1,
            sticky="ew",
            padx=(0, 12),
            pady=(2, 8),
        )

        fields[key] = entry

    form.grid_columnconfigure(1, weight=1, uniform="asset_fields")
    form.grid_columnconfigure(3, weight=1, uniform="asset_fields")

    tk.Label(
        form,
        text="Date format: YYYY-MM-DD (example: 2026-10-23)",
        bg=theme.CARD_BACKGROUND,
        fg=theme.TEXT_MUTED,
        font=(theme.FONT_FAMILY, 8),
    ).grid(
        row=3,
        column=2,
        columnspan=2,
        sticky="w",
        padx=(14, 12),
        pady=(0, 5),
    )

    # ---------------------------------------------------------
    # LOCATION, CONDITION AND STATUS
    # ---------------------------------------------------------

    make_label(
        form,
        "Location",
        size=9,
        bold=True,
    ).grid(
        row=4,
        column=0,
        sticky="w",
        padx=(14, 8),
        pady=(5, 3),
    )

    location_var = tk.StringVar(value="Unassigned")

    location_box = ttk.Combobox(
        form,
        textvariable=location_var,
        state="readonly",
        style="AssetRegistry.TCombobox",
        font=(theme.FONT_FAMILY, 9),
    )
    location_box.grid(
        row=4,
        column=1,
        sticky="ew",
        padx=(0, 12),
        pady=(2, 8),
    )

    make_label(
        form,
        "Condition",
        size=9,
        bold=True,
    ).grid(
        row=4,
        column=2,
        sticky="w",
        padx=(14, 8),
        pady=(5, 3),
    )

    condition_var = tk.StringVar(value=CONDITIONS[0])

    condition_box = ttk.Combobox(
        form,
        textvariable=condition_var,
        values=CONDITIONS,
        state="readonly",
        style="AssetRegistry.TCombobox",
        font=(theme.FONT_FAMILY, 9),
    )
    condition_box.grid(
        row=4,
        column=3,
        sticky="ew",
        padx=(0, 12),
        pady=(2, 8),
    )

    make_label(
        form,
        "Status",
        size=9,
        bold=True,
    ).grid(
        row=5,
        column=0,
        sticky="w",
        padx=(14, 8),
        pady=(3, 3),
    )

    status_var = tk.StringVar(value=STATUSES[0])

    status_box = ttk.Combobox(
        form,
        textvariable=status_var,
        values=STATUSES,
        state="readonly",
        style="AssetRegistry.TCombobox",
        font=(theme.FONT_FAMILY, 9),
    )
    status_box.grid(
        row=5,
        column=1,
        sticky="ew",
        padx=(0, 12),
        pady=(2, 10),
    )

    # ---------------------------------------------------------
    # FORM ACTION BUTTONS
    # ---------------------------------------------------------

    buttons = tk.Frame(
        form,
        bg=theme.CARD_BACKGROUND,
    )
    buttons.grid(
        row=6,
        column=0,
        columnspan=4,
        sticky="w",
        padx=14,
        pady=(5, 14),
    )

    # ---------------------------------------------------------
    # SEARCH PANEL
    # ---------------------------------------------------------

    search_panel = tk.Frame(
        body,
        bg=theme.DASHBOARD_BACKGROUND,
    )
    search_panel.pack(
        fill="x",
        padx=18,
        pady=(0, 14),
    )

    tk.Label(
        search_panel,
        text="SEARCH ASSETS",
        bg=theme.DASHBOARD_BACKGROUND,
        fg=theme.TEXT_SECONDARY,
        font=(theme.FONT_FAMILY, 9, "bold"),
    ).pack(anchor="w", pady=(0, 6))

    search_var = tk.StringVar()

    search_border, search_entry = make_entry(
        search_panel,
        search_var,
    )
    search_border.pack(fill="x")

    # ---------------------------------------------------------
    # REGISTERED ASSETS TABLE
    # ---------------------------------------------------------

    table_panel = tk.Frame(
        body,
        bg=theme.CARD_BACKGROUND,
        highlightbackground=theme.BORDER,
        highlightthickness=1,
    )
    table_panel.pack(
        fill="both",
        expand=True,
        padx=18,
        pady=(0, 18),
    )

    tk.Label(
        table_panel,
        text="REGISTERED ASSETS",
        bg=theme.CARD_BACKGROUND,
        fg=theme.CYAN,
        font=(theme.FONT_FAMILY, 10, "bold"),
    ).pack(
        anchor="w",
        padx=12,
        pady=(12, 8),
    )

    table_container = tk.Frame(
        table_panel,
        bg=theme.CARD_BACKGROUND,
    )
    table_container.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=(0, 8),
    )

    columns = (
        "id",
        "code",
        "name",
        "category",
        "location",
        "condition",
        "status",
        "purchase_date",
    )

    headings = (
        "ID",
        "ASSET CODE",
        "ASSET NAME",
        "CATEGORY",
        "LOCATION",
        "CONDITION",
        "STATUS",
        "PURCHASE DATE",
    )

    widths = (45, 100, 145, 100, 125, 90, 140, 115)

    table = ttk.Treeview(
        table_container,
        columns=columns,
        show="headings",
        selectmode="browse",
        style="AssetRegistry.Treeview",
    )

    for column, heading, width in zip(columns, headings, widths):
        table.heading(column, text=heading)
        table.column(
            column,
            width=width,
            minwidth=55,
            anchor="w",
        )

    vertical_scroll = ttk.Scrollbar(
        table_container,
        orient="vertical",
        command=table.yview,
    )

    horizontal_scroll = ttk.Scrollbar(
        table_panel,
        orient="horizontal",
        command=table.xview,
    )

    table.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set,
    )

    table.pack(side="left", fill="both", expand=True)
    vertical_scroll.pack(side="right", fill="y")

    horizontal_scroll.pack(
        fill="x",
        padx=8,
        pady=(0, 8),
    )

    # ---------------------------------------------------------
    # LOAD LOCATIONS FROM DATABASE
    # ---------------------------------------------------------

    def load_locations():
        location_map.clear()

        try:
            with connect() as connection:
                rows = connection.execute(
                    """
                    SELECT location_id, building, floor, room
                    FROM locations
                    ORDER BY building, floor, room
                    """
                ).fetchall()

            labels = ["Unassigned"]

            for location_id, building, floor, room in rows:
                label = " / ".join(
                    str(part)
                    for part in (building, floor, room)
                    if part not in (None, "")
                )

                if not label:
                    label = f"Location {location_id}"

                if label in location_map:
                    label = f"{label} (ID {location_id})"

                location_map[label] = location_id
                labels.append(label)

            location_box["values"] = labels
            location_var.set("Unassigned")

        except sqlite3.Error as error:
            show_database_error(error)

    # ---------------------------------------------------------
    # REFRESH ASSET TABLE
    # ---------------------------------------------------------

    def refresh_table():
        for item in table.get_children():
            table.delete(item)

        search = f"%{search_var.get().strip()}%"

        try:
            with connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        a.asset_id,
                        a.asset_code,
                        a.asset_name,
                        a.category,
                        COALESCE(
                            l.building,
                            'Unassigned'
                        ),
                        a.asset_condition,
                        a.status,
                        COALESCE(a.purchase_date, '')
                    FROM assets AS a
                    LEFT JOIN locations AS l
                        ON l.location_id = a.location_id
                    WHERE a.asset_code LIKE ?
                       OR a.asset_name LIKE ?
                       OR a.category LIKE ?
                    ORDER BY a.asset_id DESC
                    """,
                    (search, search, search),
                ).fetchall()

            for row in rows:
                table.insert("", "end", values=row)

        except sqlite3.Error as error:
            show_database_error(error)

    # ---------------------------------------------------------
    # CLEAR FORM
    # ---------------------------------------------------------

    def clear_form():
        selected_id["value"] = None

        for entry in fields.values():
            entry.delete(0, "end")

        condition_var.set(CONDITIONS[0])
        status_var.set(STATUSES[0])
        location_var.set("Unassigned")

        selection = table.selection()

        if selection:
            table.selection_remove(*selection)

    # ---------------------------------------------------------
    # SAVE OR UPDATE ASSET
    # ---------------------------------------------------------

    def save_asset():
        code = fields["asset_code"].get().strip()
        name = fields["asset_name"].get().strip()
        category = fields["category"].get().strip()
        purchase_date = (
            fields["purchase_date"].get().strip() or None
        )

        if not code or not name or not category:
            messagebox.showwarning(
                "Missing Information",
                "Asset code, asset name, and category are required.",
                parent=parent,
            )
            return

        if purchase_date:
            try:
                date.fromisoformat(purchase_date)
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Use YYYY-MM-DD for the purchase date.",
                    parent=parent,
                )
                fields["purchase_date"].focus_set()
                return

        location_id = location_map.get(location_var.get())

        values = (
            code,
            name,
            category,
            location_id,
            condition_var.get(),
            status_var.get(),
            purchase_date,
        )

        try:
            with connect() as connection:
                if selected_id["value"] is None:
                    connection.execute(
                        """
                        INSERT INTO assets (
                            asset_code,
                            asset_name,
                            category,
                            location_id,
                            asset_condition,
                            status,
                            purchase_date
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        values,
                    )

                    message = "Asset registered successfully."

                else:
                    connection.execute(
                        """
                        UPDATE assets
                        SET asset_code = ?,
                            asset_name = ?,
                            category = ?,
                            location_id = ?,
                            asset_condition = ?,
                            status = ?,
                            purchase_date = ?
                        WHERE asset_id = ?
                        """,
                        values + (selected_id["value"],),
                    )

                    message = "Asset updated successfully."

            clear_form()
            refresh_table()

            messagebox.showinfo(
                "Success",
                message,
                parent=parent,
            )

        except sqlite3.IntegrityError as error:
            messagebox.showerror(
                "Could Not Save",
                "The asset code may already exist, or another "
                "database constraint was not satisfied.\n\n"
                + str(error),
                parent=parent,
            )

        except sqlite3.Error as error:
            show_database_error(error)

    # ---------------------------------------------------------
    # LOAD SELECTED ASSET FOR EDITING
    # ---------------------------------------------------------

    def load_selected(event=None):
        selection = table.selection()

        if not selection:
            return

        row = table.item(selection[0], "values")
        asset_id = int(row[0])

        try:
            with connect() as connection:
                data = connection.execute(
                    """
                    SELECT
                        asset_code,
                        asset_name,
                        category,
                        purchase_date,
                        location_id,
                        asset_condition,
                        status
                    FROM assets
                    WHERE asset_id = ?
                    """,
                    (asset_id,),
                ).fetchone()

            if data is None:
                return

            selected_id["value"] = asset_id

            keys = (
                "asset_code",
                "asset_name",
                "category",
                "purchase_date",
            )

            values_to_fill = (
                data[0],
                data[1],
                data[2],
                data[3] or "",
            )

            for key, value in zip(keys, values_to_fill):
                fields[key].delete(0, "end")
                fields[key].insert(0, value)

            matching_location = next(
                (
                    label
                    for label, location_id in location_map.items()
                    if location_id == data[4]
                ),
                "Unassigned",
            )

            location_var.set(matching_location)
            condition_var.set(data[5] or CONDITIONS[0])
            status_var.set(data[6] or STATUSES[0])

        except sqlite3.Error as error:
            show_database_error(error)

    # ---------------------------------------------------------
    # DELETE SELECTED ASSET
    # ---------------------------------------------------------

    def delete_asset():
        selection = table.selection()

        if not selection:
            messagebox.showwarning(
                "Select Asset",
                "Select an asset from the table first.",
                parent=parent,
            )
            return

        row = table.item(selection[0], "values")
        asset_id = int(row[0])

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete asset {row[1]} — {row[2]}?\n\n"
            "This action cannot be undone.",
            parent=parent,
        )

        if not confirmed:
            return

        try:
            with connect() as connection:
                connection.execute(
                    "DELETE FROM assets WHERE asset_id = ?",
                    (asset_id,),
                )

            clear_form()
            refresh_table()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Cannot Delete",
                "This asset has maintenance records linked to it. "
                "Keep its history and change its status instead.",
                parent=parent,
            )

        except sqlite3.Error as error:
            show_database_error(error)

    # ---------------------------------------------------------
    # CONNECT BUTTONS
    # ---------------------------------------------------------

    make_button(
        buttons,
        "Save / Update",
        save_asset,
        theme.PRIMARY,
    ).pack(side="left", padx=(0, 7))

    make_button(
        buttons,
        "Clear Form",
        clear_form,
        theme.CARD_BACKGROUND_ALT,
    ).pack(side="left", padx=(0, 7))

    make_button(
        buttons,
        "Delete Selected",
        delete_asset,
        theme.ERROR,
    ).pack(side="left")

    # ---------------------------------------------------------
    # EVENTS AND INITIAL DATA
    # ---------------------------------------------------------

    search_entry.bind(
        "<KeyRelease>",
        lambda event: refresh_table(),
    )

    table.bind(
        "<<TreeviewSelect>>",
        load_selected,
    )

    load_locations()
    refresh_table()

    # Ensure the title bar and resize handles remain on top.
    for handle in getattr(
        parent,
        "_bubtops_resize_handles",
        [],
    ):
        if handle.winfo_exists():
            handle.lift()

    bind_mousewheel(body)
 