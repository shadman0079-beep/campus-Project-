
# BubtOps - Asset Registry
# Improved dark theme with clearly visible input fields.

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
    "Out of Service"
)

FIELD_BG = "#1B2F4B"
FIELD_BORDER = "#426080"
FIELD_FOCUS = "#2B82FF"
BUTTON_TEXT = "#FFFFFF"


def show_asset_registry(parent):
    """Open the Asset Registry window."""

    page = tk.Toplevel(parent)
    page.title("BubtOps | Asset Registry")
    page.geometry("1150x760")
    page.minsize(900, 620)
    page.configure(bg=theme.DASHBOARD_BACKGROUND)

    selected_id = {"value": None}
    location_map = {}

    def connect():
        db = sqlite3.connect(DATABASE_PATH)
        db.execute("PRAGMA foreign_keys = ON")
        return db

    # ---------- WINDOW STYLE ----------

    style = ttk.Style(page)
    style.theme_use("clam")

    style.configure(
        "BubtOps.TCombobox",
        fieldbackground=FIELD_BG,
        background=FIELD_BG,
        foreground=theme.TEXT_PRIMARY,
        arrowcolor=theme.CYAN,
        bordercolor=FIELD_BORDER,
        lightcolor=FIELD_BORDER,
        darkcolor=FIELD_BORDER,
        padding=(8, 8),
        arrowsize=14
    )

    style.map(
        "BubtOps.TCombobox",
        fieldbackground=[("readonly", FIELD_BG)],
        foreground=[("readonly", theme.TEXT_PRIMARY)],
        selectbackground=[("readonly", FIELD_BG)],
        selectforeground=[("readonly", theme.TEXT_PRIMARY)],
        bordercolor=[
            ("focus", FIELD_FOCUS),
            ("!focus", FIELD_BORDER)
        ]
    )

    style.configure(
        "BubtOps.Treeview",
        background=theme.CARD_BACKGROUND,
        fieldbackground=theme.CARD_BACKGROUND,
        foreground=theme.TEXT_PRIMARY,
        rowheight=34,
        borderwidth=0,
        font=(theme.FONT_FAMILY, 9)
    )

    style.configure(
        "BubtOps.Treeview.Heading",
        background=theme.CARD_BACKGROUND_ALT,
        foreground=theme.CYAN,
        font=(theme.FONT_FAMILY, 9, "bold"),
        relief="flat",
        padding=8
    )

    style.map(
        "BubtOps.Treeview",
        background=[("selected", theme.PRIMARY)],
        foreground=[("selected", "#FFFFFF")]
    )

    # ---------- REUSABLE UI HELPERS ----------

    def make_label(parent_frame, text, color=None, size=9, bold=False):
        return tk.Label(
            parent_frame,
            text=text,
            bg=parent_frame.cget("bg"),
            fg=color or theme.TEXT_SECONDARY,
            font=(
                theme.FONT_FAMILY,
                size,
                "bold" if bold else "normal"
            )
        )

   
    def make_entry(parent_frame, variable=None):
        """Create an input with a visible border and focus highlight."""

        border = tk.Frame(
            parent_frame,
            bg=FIELD_BORDER,
            padx=1,
            pady=1
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
            justify="left"
        )

        entry.pack(
            fill="both",
            expand=True,
            padx=7,
            ipady=5
        )

        def focus_in(event):
            border.configure(bg=FIELD_FOCUS)

        def focus_out(event):
            border.configure(bg=FIELD_BORDER)

        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)

        return border, entry


    def make_button(parent_frame, label, command, color, width=None):
        button = tk.Button(
            parent_frame,
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
            padx=15,
            pady=9,
            width=width
        )

        button.pack(side="left", padx=(0, 9))
        return button

    # ---------- PAGE HEADER ----------

    header = tk.Frame(page, bg=theme.DASHBOARD_BACKGROUND)
    header.pack(fill="x", padx=26, pady=(22, 18))

    tk.Label(
        header,
        text="Asset Registry",
        bg=theme.DASHBOARD_BACKGROUND,
        fg=theme.TEXT_PRIMARY,
        font=(theme.FONT_FAMILY, 24, "bold")
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Register, search, update and manage campus assets.",
        bg=theme.DASHBOARD_BACKGROUND,
        fg=theme.TEXT_SECONDARY,
        font=(theme.FONT_FAMILY, 10)
    ).pack(anchor="w", pady=(5, 0))

    # ---------- ASSET FORM PANEL ----------

    form = tk.Frame(
        page,
        bg=theme.CARD_BACKGROUND,
        highlightbackground=theme.BORDER,
        highlightthickness=1
    )
    form.pack(fill="x", padx=26, pady=(0, 16))

    tk.Label(
        form,
        text="ASSET DETAILS",
        bg=theme.CARD_BACKGROUND,
        fg=theme.CYAN,
        font=(theme.FONT_FAMILY, 10, "bold")
    ).grid(
        row=0, column=0, columnspan=4,
        sticky="w", padx=18, pady=(16, 13)
    )

    fields = {}

    # Two columns of labeled text fields.
    field_info = [
        ("Asset Code *", "asset_code"),
        ("Asset Name *", "asset_name"),
        ("Category *", "category"),
        ("Purchase Date", "purchase_date")
    ]

    for index, (label_text, key) in enumerate(field_info):
        row_number = 1 + index // 2
        column_number = (index % 2) * 2

        make_label(
            form, label_text, size=9, bold=True
        ).grid(
            row=row_number,
            column=column_number,
            sticky="w",
            padx=(18, 12),
            pady=(5, 2)
        )

        border, entry = make_entry(form)

        border.grid(
            row=row_number,
            column=column_number + 1,
            sticky="ew",
            padx=(0, 18),
            pady=(2, 9)
        )

        fields[key] = entry

    form.grid_columnconfigure(1, weight=1, uniform="form")
    form.grid_columnconfigure(3, weight=1, uniform="form")

    # Date hint
    tk.Label(
        form,
        text="Format: YYYY-MM-DD (example: 2026-10-23)",
        bg=theme.CARD_BACKGROUND,
        fg=theme.TEXT_MUTED,
        font=(theme.FONT_FAMILY, 8)
    ).grid(
        row=3, column=3,
        sticky="w", padx=(0, 18), pady=(0, 4)
    )

    # ---------- LOCATION, CONDITION AND STATUS ----------

    make_label(
        form, "Location", size=9, bold=True
    ).grid(
        row=3, column=0, sticky="w",
        padx=(18, 12), pady=(8, 3)
    )

    location_var = tk.StringVar(value="Unassigned")

    location_box = ttk.Combobox(
        form,
        textvariable=location_var,
        state="readonly",
        style="BubtOps.TCombobox",
        font=(theme.FONT_FAMILY, 10)
    )
    location_box.grid(
        row=3, column=1, sticky="ew",
        padx=(0, 18), pady=(3, 10)
    )

    make_label(
        form, "Condition", size=9, bold=True
    ).grid(
        row=3, column=2, sticky="w",
        padx=(18, 12), pady=(8, 3)
    )

    condition_var = tk.StringVar(value=CONDITIONS[0])

    condition_box = ttk.Combobox(
        form,
        textvariable=condition_var,
        values=CONDITIONS,
        state="readonly",
        style="BubtOps.TCombobox",
        font=(theme.FONT_FAMILY, 10)
    )
    condition_box.grid(
        row=3, column=3, sticky="ew",
        padx=(0, 18), pady=(3, 10)
    )

    make_label(
        form, "Status", size=9, bold=True
    ).grid(
        row=4, column=0, sticky="w",
        padx=(18, 12), pady=(3, 3)
    )

    status_var = tk.StringVar(value=STATUSES[0])

    status_box = ttk.Combobox(
        form,
        textvariable=status_var,
        values=STATUSES,
        state="readonly",
        style="BubtOps.TCombobox",
        font=(theme.FONT_FAMILY, 10)
    )
    status_box.grid(
        row=4, column=1, sticky="ew",
        padx=(0, 18), pady=(3, 12)
    )

    # ---------- FORM ACTION BUTTONS ----------

    buttons = tk.Frame(form, bg=theme.CARD_BACKGROUND)
    buttons.grid(
        row=5, column=0, columnspan=4,
        sticky="w", padx=18, pady=(7, 17)
    )

    # ---------- SEARCH PANEL ----------

    search_panel = tk.Frame(
        page,
        bg=theme.DASHBOARD_BACKGROUND
    )
    search_panel.pack(fill="x", padx=26, pady=(0, 13))

    tk.Label(
        search_panel,
        text="SEARCH ASSETS",
        bg=theme.DASHBOARD_BACKGROUND,
        fg=theme.TEXT_SECONDARY,
        font=(theme.FONT_FAMILY, 9, "bold")
    ).pack(anchor="w", pady=(0, 6))

    search_var = tk.StringVar()

    search_border, search_entry = make_entry(
        search_panel, search_var
    )
    search_border.pack(fill="x")

    # ---------- ASSET TABLE ----------

    table_panel = tk.Frame(
        page,
        bg=theme.CARD_BACKGROUND,
        highlightbackground=theme.BORDER,
        highlightthickness=1
    )
    table_panel.pack(
        fill="both", expand=True,
        padx=26, pady=(0, 22)
    )

    tk.Label(
        table_panel,
        text="REGISTERED ASSETS",
        bg=theme.CARD_BACKGROUND,
        fg=theme.CYAN,
        font=(theme.FONT_FAMILY, 10, "bold")
    ).pack(anchor="w", padx=14, pady=(12, 8))

    table_container = tk.Frame(
        table_panel,
        bg=theme.CARD_BACKGROUND
    )
    table_container.pack(
        fill="both", expand=True, padx=10, pady=(0, 10)
    )

    columns = (
        "id", "code", "name", "category",
        "location", "condition", "status", "purchase_date"
    )

    headings = (
        "ID", "ASSET CODE", "ASSET NAME", "CATEGORY",
        "LOCATION", "CONDITION", "STATUS", "PURCHASE DATE"
    )

    widths = (45, 105, 155, 110, 150, 95, 145, 120)

    table = ttk.Treeview(
        table_container,
        columns=columns,
        show="headings",
        selectmode="browse",
        style="BubtOps.Treeview"
    )

    for column, heading, width in zip(columns, headings, widths):
        table.heading(column, text=heading)
        table.column(
            column,
            width=width,
            minwidth=45,
            anchor="w"
        )

    vertical_scroll = ttk.Scrollbar(
        table_container,
        orient="vertical",
        command=table.yview
    )
    horizontal_scroll = ttk.Scrollbar(
        table_panel,
        orient="horizontal",
        command=table.xview
    )

    table.configure(
        yscrollcommand=vertical_scroll.set,
        xscrollcommand=horizontal_scroll.set
    )

    table.pack(side="left", fill="both", expand=True)
    vertical_scroll.pack(side="right", fill="y")
    horizontal_scroll.pack(fill="x", padx=10, pady=(0, 8))

    # ---------- LOAD LOCATIONS ----------

    def load_locations():
        location_map.clear()

        try:
            with connect() as db:
                rows = db.execute(
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
                    if part
                )

                if label in location_map:
                    label = f"{label} (ID {location_id})"

                location_map[label] = location_id
                labels.append(label)

            location_box["values"] = labels
            location_var.set("Unassigned")

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error", str(error), parent=page
            )

    # ---------- REFRESH TABLE ----------

    def refresh_table():
        for item in table.get_children():
            table.delete(item)

        search = f"%{search_var.get().strip()}%"

        try:
            with connect() as db:
                rows = db.execute(
                    """
                    SELECT
                        a.asset_id,
                        a.asset_code,
                        a.asset_name,
                        a.category,
                        COALESCE(l.building, 'Unassigned'),
                        a.asset_condition,
                        a.status,
                        COALESCE(a.purchase_date, '')
                    FROM assets AS a
                    LEFT JOIN locations AS l
                        ON l.location_id = a.location_id
                    WHERE a.asset_code LIKE ?
                       OR a.asset_name LIKE ?
                    ORDER BY a.asset_id DESC
                    """,
                    (search, search)
                ).fetchall()

            for row in rows:
                table.insert("", "end", values=row)

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error", str(error), parent=page
            )

    # ---------- CLEAR FORM ----------

    def clear_form():
        selected_id["value"] = None

        for entry in fields.values():
            entry.delete(0, "end")

        condition_var.set(CONDITIONS[0])
        status_var.set(STATUSES[0])
        location_var.set("Unassigned")

        table.selection_remove(table.selection())

    # ---------- SAVE OR UPDATE ASSET ----------

    def save_asset():
        code = fields["asset_code"].get().strip()
        name = fields["asset_name"].get().strip()
        category = fields["category"].get().strip()
        purchase_date = fields["purchase_date"].get().strip() or None

        if not code or not name or not category:
            messagebox.showwarning(
                "Missing Information",
                "Asset code, asset name, and category are required.",
                parent=page
            )
            return

        if purchase_date:
            try:
                date.fromisoformat(purchase_date)
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date",
                    "Use YYYY-MM-DD for the purchase date.",
                    parent=page
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
            purchase_date
        )

        try:
            with connect() as db:
                if selected_id["value"] is None:
                    db.execute(
                        """
                        INSERT INTO assets (
                            asset_code, asset_name, category,
                            location_id, asset_condition,
                            status, purchase_date
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        values
                    )
                    message = "Asset registered successfully."

                else:
                    db.execute(
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
                        values + (selected_id["value"],)
                    )
                    message = "Asset updated successfully."

            messagebox.showinfo(
                "Success", message, parent=page
            )

            clear_form()
            refresh_table()

        except sqlite3.IntegrityError as error:
            messagebox.showerror(
                "Could Not Save",
                "The asset code may already exist.\n\n" + str(error),
                parent=page
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error", str(error), parent=page
            )

    # ---------- SELECT ASSET FOR EDITING ----------

    def load_selected(event=None):
        selection = table.selection()

        if not selection:
            return

        row = table.item(selection[0], "values")
        asset_id = int(row[0])

        try:
            with connect() as db:
                data = db.execute(
                    """
                    SELECT asset_code, asset_name, category,
                           purchase_date, location_id,
                           asset_condition, status
                    FROM assets
                    WHERE asset_id = ?
                    """,
                    (asset_id,)
                ).fetchone()

            if data is None:
                return

            selected_id["value"] = asset_id

            keys = (
                "asset_code",
                "asset_name",
                "category",
                "purchase_date"
            )
            values_to_fill = (
                data[0],
                data[1],
                data[2],
                data[3] or ""
            )

            for key, value in zip(keys, values_to_fill):
                fields[key].delete(0, "end")
                fields[key].insert(0, value)

            location_var.set(
                next(
                    (
                        label
                        for label, loc_id in location_map.items()
                        if loc_id == data[4]
                    ),
                    "Unassigned"
                )
            )

            condition_var.set(data[5])
            status_var.set(data[6])

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error", str(error), parent=page
            )

    # ---------- DELETE ASSET ----------

    def delete_asset():
        selection = table.selection()

        if not selection:
            messagebox.showwarning(
                "Select Asset",
                "Select an asset from the table first.",
                parent=page
            )
            return

        row = table.item(selection[0], "values")
        asset_id = int(row[0])

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete asset {row[1]} — {row[2]}?\n\n"
            "This action cannot be undone.",
            parent=page
        )

        if not confirmed:
            return

        try:
            with connect() as db:
                db.execute(
                    "DELETE FROM assets WHERE asset_id = ?",
                    (asset_id,)
                )

            clear_form()
            refresh_table()

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Cannot Delete",
                "This asset has maintenance records linked to it. "
                "Keep its history and change its status instead.",
                parent=page
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error", str(error), parent=page
            )

    # ---------- CONNECT BUTTONS ----------

    make_button(
        buttons, "Save / Update Asset",
        save_asset, theme.PRIMARY
    )
    make_button(
        buttons, "Clear Form",
        clear_form, theme.CARD_BACKGROUND_ALT
    )
    make_button(
        buttons, "Delete Selected",
        delete_asset, theme.ERROR
    )

    # ---------- EVENTS AND INITIAL DATA ----------

    search_entry.bind(
        "<KeyRelease>",
        lambda event: refresh_table()
    )
    table.bind("<<TreeviewSelect>>", load_selected)

    load_locations()
    refresh_table()

    # Put the new window in front of the dashboard.
    page.transient(parent)
    page.lift()
