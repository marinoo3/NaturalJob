import sqlite3

connection = sqlite3.connect("data/db/user.db")
cursor = connection.cursor()

schema_statements = [
    """
    CREATE TABLE IF NOT EXISTS FILE (
        uuid TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        date TEXT,
        path TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS SAVED_OFFER (
        offer_id TEXT PRIMARY KEY
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS APPLIED_OFFER (
        offer_id TEXT PRIMARY KEY
    )
    """
]

for stmt in schema_statements:
    cursor.execute(stmt)

connection.commit()
connection.close()