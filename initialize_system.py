import sqlite3
import os
from pathlib import Path
import shutil

class SystemInitializer:
    def __init__(self):
        self.db_path = 'cafe_manager.db'
        self.conn = None
        self.cursor = None

    def clean_start(self):
        """Remove existing database and create fresh"""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print("Removed existing database")
        except Exception as e:
            print(f"Error cleaning up: {e}")

    def initialize_database(self):
        """Create and initialize database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Enable foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create all tables in correct order
            self.create_base_tables()
            self.create_operational_tables()
            self.create_tracking_tables()
            
            # Insert default data
            self.insert_default_data()
            
            # Verify setup
            self.verify_setup()
            
            print("System initialization complete!")
            
        except Exception as e:
            print(f"Initialization error: {e}")
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print("Cleaned up failed initialization")
        finally:
            if self.conn:
                self.conn.close()

    def create_base_tables(self):
        """Create fundamental tables"""
        self.cursor.executescript('''
            -- Users table
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Menu Categories
            CREATE TABLE IF NOT EXISTS menu_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            -- Menu Items
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category_id INTEGER,
                price REAL NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES menu_categories (id)
            );

            -- Tables
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER UNIQUE NOT NULL,
                status TEXT CHECK(status IN ('vacant', 'occupied')) DEFAULT 'vacant',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.conn.commit()
        print("Base tables created")

    def create_operational_tables(self):
        """Create operation-related tables"""
        self.cursor.executescript('''
            -- Sales
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
            );

            -- Sale Items
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
            );

            -- Bar Stock
            CREATE TABLE IF NOT EXISTS bar_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL UNIQUE,
                quantity INTEGER NOT NULL DEFAULT 0,
                min_threshold INTEGER NOT NULL DEFAULT 10,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Staff
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                contact TEXT,
                salary REAL NOT NULL,
                join_date DATE DEFAULT CURRENT_DATE,
                status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
                last_paid DATE
            );

            -- Staff Payments
            CREATE TABLE IF NOT EXISTS staff_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE DEFAULT CURRENT_DATE,
                notes TEXT,
                FOREIGN KEY (staff_id) REFERENCES staff (id)
            );
        ''')
        self.conn.commit()
        print("Operational tables created")

    def create_tracking_tables(self):
        """Create tracking and history tables"""
        self.cursor.executescript('''
            -- Stock History
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                change_quantity INTEGER NOT NULL,
                operation_type TEXT CHECK(operation_type IN ('add', 'remove')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES bar_stock (id)
            );

            -- Expenses
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit REAL NOT NULL,
                total_price REAL NOT NULL,
                expense_date DATE DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        self.conn.commit()
        print("Tracking tables created")

    def insert_default_data(self):
        """Insert necessary default data"""
        try:
            # Default admin
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (username, password)
                VALUES (?, ?)
            ''', ('admin', 'admin123'))

            # Default tables
            for i in range(1, 16):
                self.cursor.execute('''
                    INSERT OR IGNORE INTO tables (table_number)
                    VALUES (?)
                ''', (i,))

            # Default categories
            categories = ['Beverages', 'Food', 'Desserts']
            for cat in categories:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO menu_categories (name)
                    VALUES (?)
                ''', (cat,))

            # Default menu items
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

            # Default bar stock items
            default_stock = [
                ('Beer', 50, 20),
                ('Wine', 30, 10),
                ('Whiskey', 20, 5),
                ('Vodka', 25, 8),
                ('Rum', 15, 5)
            ]
            for name, qty, threshold in default_stock:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO bar_stock (item_name, quantity, min_threshold)
                    VALUES (?, ?, ?)
                ''', (name, qty, threshold))

            self.conn.commit()
            print("Default data inserted")

        except sqlite3.Error as e:
            print(f"Error inserting default data: {e}")
            raise

    def verify_setup(self):
        """Verify all tables and initial data"""
        required_tables = [
            'users', 'menu_categories', 'menu_items', 'tables',
            'sales', 'sale_items', 'bar_stock', 'stock_history', 
            'staff', 'staff_payments', 'expenses'
        ]

        for table in required_tables:
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not self.cursor.fetchone():
                raise Exception(f"Required table {table} is missing!")

        print("\nVerification complete - All tables exist:")
        for table in required_tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            print(f"- {table}: {count} rows")

def main():
    print("Starting system initialization...")
    initializer = SystemInitializer()
    initializer.clean_start()  # Remove existing database
    initializer.initialize_database()
    print("\nSystem initialization complete!")

if __name__ == "__main__":
    main() 