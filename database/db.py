
# database/db.py

import sqlite3
from pathlib import Path


# Keep the database in G:\BubtOps,
# not inside the database subfolder.
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_FOLDER / "bubtops.db"


def setup_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS locations (
                location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                building TEXT NOT NULL,
                floor TEXT,
                room TEXT
            );

            CREATE TABLE IF NOT EXISTS assets (
                asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_code TEXT NOT NULL UNIQUE,
                asset_name TEXT NOT NULL,
                category TEXT NOT NULL,
                location_id INTEGER,
                asset_condition TEXT NOT NULL,
                status TEXT NOT NULL,
                purchase_date TEXT,
                FOREIGN KEY (location_id)
                    REFERENCES locations(location_id)
            );

            CREATE TABLE IF NOT EXISTS maintenance_records (
                maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                user_id INTEGER,
                maintenance_date TEXT NOT NULL,
                description TEXT NOT NULL,
                cost REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL,
                FOREIGN KEY (asset_id)
                    REFERENCES assets(asset_id),
                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
            );
        """)
