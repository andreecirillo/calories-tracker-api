import sqlite3
import os
from models import Base, engine

def import_data():
    # Initialize the database
    print("Initializing database...")
    db_file = 'calories.db'
    
    # Remove existing database file if it exists
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("Reading data from calories.sql...")
    with open('calories.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Split the script into individual INSERT statements
    insert_statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
    
    print(f"Found {len(insert_statements)} INSERT statements to execute...")
    
    # Execute each INSERT statement
    for i, stmt in enumerate(insert_statements, 1):
        try:
            cursor.execute(stmt + ';')
            if i % 5 == 0 or i == len(insert_statements):
                print(f"Processed {i}/{len(insert_statements)} statements...")
        except sqlite3.Error as e:
            print(f"Error executing statement {i}: {e}")
            print(f"Statement: {stmt}")
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print(f"Data import completed successfully! Database file: {os.path.abspath(db_file)}")

if __name__ == "__main__":
    import_data()
