import sqlite3
import os
import traceback

# Debug prints to show database location
print(f"Current working directory: {os.getcwd()}")
print(f"Database will be created at: {os.path.abspath('cafe_manager.db')}")

def initialize_database():
    try:
        print("Step 1: Checking for existing database...")
        # Remove existing database if any
        if os.path.exists('cafe_manager.db'):
            os.remove('cafe_manager.db')
            print("Removed existing database")
        
        print("Step 2: Creating new database connection...")
        conn = sqlite3.connect('cafe_manager.db')
        cursor = conn.cursor()
        
        try:
            print("Step 3: Enabling foreign keys...")
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            print("Step 4: Creating independent tables...")
            # 1. Independent Tables First
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            ''')
            print("- Created users table")
            
            cursor.execute('''
                CREATE TABLE tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER UNIQUE NOT NULL,
                    status TEXT CHECK(status IN ('vacant', 'occupied')) DEFAULT 'vacant',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("- Created tables table")
            
            cursor.execute('''
                CREATE TABLE menu_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            print("- Created menu_categories table")
            
            cursor.execute('''
                CREATE TABLE bar_stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL UNIQUE,
                    quantity INTEGER NOT NULL,
                    min_threshold INTEGER NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("- Created bar_stock table")

            cursor.execute('''
                CREATE TABLE expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price_per_unit REAL NOT NULL,
                    total_price REAL NOT NULL,
                    expense_date DATE DEFAULT CURRENT_DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("- Created expenses table")
            
            print("Step 5: Creating dependent tables...")
            # 2. Dependent Tables Next
            cursor.execute('''
                CREATE TABLE menu_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (category_id) REFERENCES menu_categories (id)
                )
            ''')
            print("- Created menu_items table")
            
            cursor.execute('''
                CREATE TABLE sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER NOT NULL,
                    subtotal REAL NOT NULL,
                    discount_type TEXT CHECK(discount_type IN ('percentage', 'amount')),
                    discount_value REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    payment_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (table_number) REFERENCES tables (table_number)
                )
            ''')
            print("- Created sales table")
            
            cursor.execute('''
                CREATE TABLE sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    menu_item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price_per_unit REAL NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
                )
            ''')
            print("- Created sale_items table")
            
            cursor.execute('''
                CREATE TABLE stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    change_quantity INTEGER NOT NULL,
                    operation_type TEXT CHECK(operation_type IN ('add', 'remove')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES bar_stock (id)
                )
            ''')
            print("- Created stock_history table")
            
            print("Step 6: Inserting default data...")
            # 3. Insert Default Data
            
            # Admin user
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                        ('admin', 'pass'))
            print("- Inserted admin user")
            
            # Default tables (1-15)
            for i in range(1, 16):
                cursor.execute('INSERT INTO tables (table_number) VALUES (?)', (i,))
            print("- Inserted default tables")
            
            # Default categories
            categories = ['Food', 'Drinks', 'Snacks']
            for category in categories:
                cursor.execute('INSERT INTO menu_categories (name) VALUES (?)', 
                            (category,))
            print("- Inserted default categories")
            
            # Commit all changes
            print("Step 7: Committing changes...")
            conn.commit()
            
            print("Step 8: Verifying setup...")
            # 4. Verify Setup
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("\nVerification - Created tables:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"- {table[0]}: {count} rows")
            
            print("\nDatabase initialization complete!")
            
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
            print("Traceback:")
            traceback.print_exc()
            conn.rollback()
            raise
        finally:
            conn.close()
            print("Database connection closed")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Traceback:")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("Starting database initialization...")
    initialize_database() 