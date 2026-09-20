import sqlite3
from datetime import datetime

def init_db():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('calories.db')
    cursor = conn.cursor()
    
    # Create the food_entries_foodentry table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_entries_foodentry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        food_name TEXT,
        calories INTEGER,
        date_time DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Commit the changes
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
