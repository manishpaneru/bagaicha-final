import sqlite3
from pathlib import Path

def create_all_tables():
    """Create all necessary database tables"""
    try:
        conn = sqlite3.connect('cafe_manager.db')
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create menu_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Create menu_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                price REAL NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES menu_categories (id)
            )
        ''')
        
        # Create tables table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER UNIQUE NOT NULL,
                status TEXT CHECK(status IN ('vacant', 'occupied')) DEFAULT 'vacant',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                discount_type TEXT CHECK(discount_type IN ('percentage', 'amount')),
                discount_value REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                payment_status TEXT CHECK(payment_status IN ('pending', 'completed')) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_number) REFERENCES tables (table_number)
            )
        ''')
        
        # Create sale_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit REAL NOT NULL,
                total_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
            )
        ''')

        # Create bar_stock table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bar_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                current_stock INTEGER NOT NULL DEFAULT 0,
                min_threshold INTEGER NOT NULL DEFAULT 10,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create stock_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                operation_type TEXT CHECK(operation_type IN ('add', 'remove')) NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES bar_stock (id)
            )
        ''')

        # Create staff table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                contact TEXT,
                salary REAL NOT NULL,
                join_date DATE DEFAULT CURRENT_DATE,
                status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
                last_paid DATE
            )
        ''')

        # Create staff_payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE DEFAULT CURRENT_DATE,
                notes TEXT,
                FOREIGN KEY (staff_id) REFERENCES staff (id)
            )
        ''')

        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
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
        
        # Insert default tables (1-15)
        for table_num in range(1, 16):
            cursor.execute('''
                INSERT OR IGNORE INTO tables (table_number)
                VALUES (?)
            ''', (table_num,))

        # Insert default menu categories
        default_categories = ['Beverages', 'Food', 'Desserts']
        for category in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO menu_categories (name)
                VALUES (?)
            ''', (category,))

        # Insert default menu items
        default_items = [
            ('Coffee', 'Beverages', 120.0),
            ('Tea', 'Beverages', 80.0),
            ('Sandwich', 'Food', 150.0),
            ('Pasta', 'Food', 200.0),
            ('Ice Cream', 'Desserts', 100.0),
            ('Cake', 'Desserts', 180.0)
        ]
        
        for item_name, category_name, price in default_items:
            cursor.execute('''
                SELECT id FROM menu_categories WHERE name = ?
            ''', (category_name,))
            category_id = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT OR IGNORE INTO menu_items (name, category_id, price)
                VALUES (?, ?, ?)
            ''', (item_name, category_id, price))
        
        conn.commit()
        print("All tables created successfully!")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nCreated tables:")
        for table in tables:
            print(f"- {table[0]}")
            
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_all_tables() 