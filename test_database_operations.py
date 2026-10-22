
import sqlite3
from database.db import DATABASE_PATH

connection = sqlite3.connect(DATABASE_PATH)
connection.execute("PRAGMA foreign_keys = ON")

try:
    # Create a temporary test location.
    cursor = connection.execute(
        """
        INSERT INTO locations (building, floor, room)
        VALUES (?, ?, ?)
        """,
        ("TEST_BUILDING", "TEST_FLOOR", "TEST_ROOM")
    )

    location_id = cursor.lastrowid

    # Create a temporary test asset.
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
        (
            "TEST-ASSET-001",
            "Test Computer",
            "Computer",
            location_id,
            "Good",
            "In Service",
            "2026-01-01"
        )
    )

    connection.commit()
    print("PASS: Test records saved.")

    # Retrieve the asset from SQLite.
    asset = connection.execute(
        """
        SELECT asset_code, asset_name, status
        FROM assets
        WHERE asset_code = ?
        """,
        ("TEST-ASSET-001",)
    ).fetchone()

    print("Retrieved asset:", asset)

    if asset == ("TEST-ASSET-001", "Test Computer", "In Service"):
        print("PASS: Saved data was retrieved correctly.")
    else:
        print("FAIL: Retrieved data did not match.")

finally:
    # Remove only the temporary test records.
    connection.execute(
        "DELETE FROM assets WHERE asset_code = ?",
        ("TEST-ASSET-001",)
    )
    connection.execute(
        """
        DELETE FROM locations
        WHERE building = ? AND floor = ? AND room = ?
        """,
        ("TEST_BUILDING", "TEST_FLOOR", "TEST_ROOM")
    )
    connection.commit()
    connection.close()
    print("Test cleanup completed.")
