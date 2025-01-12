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
                CREATE TABLE staff (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    salary REAL NOT NULL,
                    join_date DATE NOT NULL,
                    last_paid_date DATE,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("- Created staff table")
            
            cursor.execute('''
                CREATE TABLE staff_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (staff_id) REFERENCES staff (id)
                )
            ''')
            print("- Created staff_payments table")
            
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
                CREATE TABLE IF NOT EXISTS bar_stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL UNIQUE,
                    unit_type TEXT NOT NULL CHECK(unit_type IN ('ML', 'PIECE', 'PACKET')),
                    pieces_per_packet INTEGER,     -- For cigarettes (20 pieces per packet)
                    quantity REAL NOT NULL,        -- Current quantity
                    original_quantity REAL NOT NULL, -- Initial quantity when added
                    min_threshold REAL NOT NULL,   -- Warning threshold
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("- Created bar_stock table")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    change_quantity REAL NOT NULL,
                    operation_type TEXT CHECK(operation_type IN ('add', 'remove')) NOT NULL,
                    source TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES bar_stock (id)
                )
            ''')
            print("- Created stock_history table")

            # Create expense_categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expense_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')

            # Insert default categories
            default_categories = ['Management', 'Miscellaneous', 'Bar', 'Kitchen']
            for category in default_categories:
                cursor.execute('INSERT OR IGNORE INTO expense_categories (name) VALUES (?)', (category,))

            # Create expenses table with category reference
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
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
            
            # Add temporary_bills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS temporary_bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER NOT NULL,
                    menu_item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price_per_unit REAL NOT NULL,
                    total_price REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (table_number) REFERENCES tables (table_number),
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
                )
            ''')
            print("- Created temporary_bills table")
            
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
            
            # Default menu items
            # Get category IDs
            cursor.execute("SELECT id, name FROM menu_categories")
            category_ids = {name: id for id, name in cursor.fetchall()}

            # Remove existing cigarette items and category
            cursor.execute("DELETE FROM menu_categories WHERE name = 'Cigarette'")
            
            # Add cigarette category
            cursor.execute("INSERT INTO menu_categories (name) VALUES ('Cigarette')")
            cursor.execute("SELECT id FROM menu_categories WHERE name = 'Cigarette'")
            cigarette_category_id = cursor.fetchone()[0]

            # Add predefined cigarette items
            cigarette_items = [
                ("Surya Red", cigarette_category_id, 30),      # Rs 30 per piece
                ("Surya Artic", cigarette_category_id, 35),    # Rs 35 per piece
                ("Sikhar Ice", cigarette_category_id, 25)      # Rs 25 per piece
            ]

            for name, category_id, price in cigarette_items:
                cursor.execute("""
                    INSERT INTO menu_items (name, category_id, price)
                    VALUES (?, ?, ?)
                """, (name, category_id, price))
            print("- Inserted predefined cigarette items")

            # Food items
            food_items = [
                ("Chicken Momo", category_ids['Food'], 180),
                ("Veg Momo", category_ids['Food'], 160),
                ("Chowmein", category_ids['Food'], 150),
                ("Thukpa", category_ids['Food'], 170),
            ]
            for name, category_id, price in food_items:
                cursor.execute("""
                    INSERT INTO menu_items (name, category_id, price)
                    VALUES (?, ?, ?)
                """, (name, category_id, price))

            # Drinks items
            drinks_items = [
                ("Coca Cola", category_ids['Drinks'], 60),
                ("Fanta", category_ids['Drinks'], 60),
                ("Coffee", category_ids['Drinks'], 50),
                ("Tea", category_ids['Drinks'], 30),
            ]
            for name, category_id, price in drinks_items:
                cursor.execute("""
                    INSERT INTO menu_items (name, category_id, price)
                    VALUES (?, ?, ?)
                """, (name, category_id, price))

            # Snacks items
            snacks_items = [
                ("French Fries", category_ids['Snacks'], 120),
                ("Potato Chips", category_ids['Snacks'], 100),
                ("Peanuts", category_ids['Snacks'], 80),
            ]
            for name, category_id, price in snacks_items:
                cursor.execute("""
                    INSERT INTO menu_items (name, category_id, price)
                    VALUES (?, ?, ?)
                """, (name, category_id, price))

            print("- Inserted default menu items")

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