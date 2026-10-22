
import sqlite3
from database.db import setup_database, DATABASE_PATH

setup_database()

connection = sqlite3.connect(DATABASE_PATH)

tables = connection.execute(
    "SELECT name FROM sqlite_master "
    "WHERE type = 'table' ORDER BY name"
).fetchall()

print("Database path:", DATABASE_PATH)
print("Tables found:")

for table in tables:
    print("-", table[0])

connection.close()
