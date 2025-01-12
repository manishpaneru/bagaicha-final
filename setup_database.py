import sqlite3
import os
from datetime import datetime

class DatabaseSetup:
    def __init__(self, db_name="cafe_manager.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            # Enable foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            print("Database connection established")
        except sqlite3.Error as e:
            print(f"Connection Error: {e}")

    def create_all_tables(self):
        """Create all required tables"""
        try:
            # 1. Users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 2. Menu Categories table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')

            # 3. Menu Items table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    price REAL NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (category_id) REFERENCES menu_categories (id)
                )
            ''')

            # 4. Tables table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER UNIQUE NOT NULL,
                    status TEXT CHECK(status IN ('vacant', 'occupied')) DEFAULT 'vacant',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 5. Sales table
            self.cursor.execute('''
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

            # 6. Sale Items table
            self.cursor.execute('''
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

            # 7. Bar Stock table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bar_stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL UNIQUE,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    min_threshold INTEGER NOT NULL DEFAULT 10,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 8. Stock History table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    change_quantity INTEGER NOT NULL,
                    operation_type TEXT CHECK(operation_type IN ('add', 'remove')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES bar_stock (id)
                )
            ''')

            # 9. Staff table
            self.cursor.execute('''
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

            # 10. Staff Payments table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS staff_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date DATE DEFAULT CURRENT_DATE,
                    notes TEXT,
                    FOREIGN KEY (staff_id) REFERENCES staff (id)
                )
            ''')

            # 11. Expenses table
            self.cursor.execute('''
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

            self.conn.commit()
            print("All tables created successfully")

        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def insert_default_data(self):
        """Insert default data"""
        try:
            # Insert default admin user
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (username, password)
                VALUES (?, ?)
            ''', ('admin', 'admin123'))

            # Insert default tables (1-15)
            for i in range(1, 16):
                self.cursor.execute('''
                    INSERT OR IGNORE INTO tables (table_number)
                    VALUES (?)
                ''', (i,))

            # Insert default menu categories
            default_categories = ['Beverages', 'Food', 'Desserts']
            for category in default_categories:
                self.cursor.execute('''
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
                # Get category id
                self.cursor.execute('SELECT id FROM menu_categories WHERE name = ?', (category_name,))
                category_id = self.cursor.fetchone()[0]
                
                # Insert menu item
                self.cursor.execute('''
                    INSERT OR IGNORE INTO menu_items (name, category_id, price)
                    VALUES (?, ?, ?)
                ''', (item_name, category_id, price))

            self.conn.commit()
            print("Default data inserted successfully")

        except sqlite3.Error as e:
            print(f"Error inserting default data: {e}")

    def verify_tables(self):
        """Verify all tables exist"""
        try:
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table'
            """)
            tables = self.cursor.fetchall()
            print("\nExisting tables:")
            for table in tables:
                print(f"- {table[0]}")
        except sqlite3.Error as e:
            print(f"Error verifying tables: {e}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

def setup_database():
    """Main setup function"""
    # Remove existing database if it exists
    if os.path.exists("cafe_manager.db"):
        os.remove("cafe_manager.db")
        print("Removed existing database")
    
    db = DatabaseSetup()
    db.connect()
    db.create_all_tables()
    db.insert_default_data()
    db.verify_tables()
    db.close()

if __name__ == "__main__":
    setup_database() 