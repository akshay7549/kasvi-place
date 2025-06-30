import sqlite3
import os
from datetime import datetime

# Determine the database directory and path
base_dir = os.path.dirname(__file__)
db_dir = os.path.join(base_dir)
os.makedirs(db_dir, exist_ok=True)

db_path = os.path.join(db_dir, 'kasvi.db')  # You may want to rename this to 'kasvi.db' for consistency

def initialize_database():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Table for bookings
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            room_type TEXT NOT NULL,
            checkin TEXT NOT NULL,
            checkout TEXT NOT NULL
        )
    ''')

    # Table for contact messages
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with bookings and messages tables.")

if __name__ == "__main__":
    initialize_database()
