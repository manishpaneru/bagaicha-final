import sqlite3
import os

def fix_database():
    # Delete existing database if it exists
    if os.path.exists('cafe_manager.db'):
        os.remove('cafe_manager.db')
        print("Removed old database")

    # Create new connection
    conn = sqlite3.connect('cafe_manager.db')
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create sales table FIRST
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            discount_type TEXT,
            discount_value REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            payment_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Sales table created")

        # Create bar_stock table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bar_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL,
            min_threshold INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Bar stock table created")
        
        # Add some test data to ensure tables work
        cursor.execute('''
        INSERT INTO sales (table_number, subtotal, total_amount)
        VALUES (1, 100.0, 100.0)
        ''')
        
        cursor.execute('''
        INSERT INTO bar_stock (item_name, quantity, min_threshold)
        VALUES ('Test Item', 50, 10)
        ''')
        
        # Commit changes
        conn.commit()
        print("Test data inserted")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nExisting tables:")
        for table in tables:
            print(f"- {table[0]}")
            
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database fix...")
    fix_database()
    print("Database fix complete!") 