import sqlite3

def initialize_database():
    conn = sqlite3.connect("licenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_code TEXT UNIQUE,
            signature TEXT
        )
    """)
    conn.commit()
    conn.close()

initialize_database()
