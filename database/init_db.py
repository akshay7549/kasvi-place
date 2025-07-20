import sqlite3
import os
from datetime import datetime

# Determine the database directory and path
base_dir = os.path.dirname(__file__)
db_dir = os.path.join(base_dir)
os.makedirs(db_dir, exist_ok=True)

db_path = os.path.join(db_dir, 'kasvi.db')  # Make sure the file name is consistent

def initialize_database():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Table for room bookings
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

    # Table for restaurant menu
    c.execute('''
        CREATE TABLE IF NOT EXISTS restaurant_menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        )
    ''')

    # Table for restaurant table bookings
    c.execute('''
        CREATE TABLE IF NOT EXISTS table_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            guests INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized with bookings, messages, menu, and table_bookings tables.")

if __name__ == "__main__":
    initialize_database()
