"""
Database operations for the Cafe Management System.
Handles database connection, table creation, and data management.
"""

import datetime
import logging
import os
import sqlite3
from sqlite3 import Error

class DatabaseManager:
    """Manages database operations for the cafe management system."""
    
    def __init__(self, db_file="cafe_manager.db"):
        """Initialize database manager."""
        # Get absolute path to database in root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(root_dir, db_file)
        print(f"Connecting to database at: {self.db_path}")
        self.conn = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        logging.basicConfig(
            filename='logs/database.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def connect(self):
        """Create a database connection."""
        try:
            if not os.path.exists(self.db_path):
                print(f"Database not found at: {self.db_path}")
                # Run initialization if database doesn't exist
                from initialize_db import initialize_database
                initialize_database()
                
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            logging.info(f"Successfully connected to database at {self.db_path}")
            return self.conn
        except Error as e:
            logging.error(f"Error connecting to database: {str(e)}")
            print(f"Database connection error: {e}")
            return None
    
    def create_tables(self):
        """Create all required tables for the cafe management system."""
        try:
            cursor = self.conn.cursor()
            
            # 1. Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. Menu categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            
            # 3. Menu items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    price REAL NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES menu_categories(id),
                    UNIQUE (name, category_id)
                )
            ''')
            
            # 4. Tables table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER UNIQUE NOT NULL,
                    status TEXT CHECK(status IN ('vacant', 'occupied')) DEFAULT 'vacant',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 5. Sales table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_number INTEGER,
                    subtotal REAL NOT NULL,
                    discount_type TEXT CHECK(discount_type IN ('percentage', 'amount')),
                    discount_value REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    payment_status TEXT CHECK(payment_status IN ('pending', 'completed')) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (table_number) REFERENCES tables(table_number)
                )
            ''')
            
            # 6. Sale items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER,
                    menu_item_id INTEGER,
                    quantity INTEGER NOT NULL,
                    price_per_unit REAL NOT NULL,
                    total_price REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
                )
            ''')
            
            # 7. Expenses table
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
            
            # 8. Staff table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS staff (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    salary REAL NOT NULL,
                    join_date DATE NOT NULL,
                    last_paid_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 9. Staff payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS staff_payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    staff_id INTEGER,
                    amount REAL NOT NULL,
                    payment_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (staff_id) REFERENCES staff(id)
                )
            ''')
            
            # 10. Bar stock table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bar_stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL UNIQUE,
                    quantity INTEGER NOT NULL,
                    min_threshold INTEGER NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 11. Stock history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER,
                    change_quantity INTEGER NOT NULL,
                    operation_type TEXT CHECK(operation_type IN ('add', 'remove')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES bar_stock(id)
                )
            ''')
            
            # Create indexes for frequently queried columns
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_history_item ON stock_history(item_id)')
            
            self.conn.commit()
            logging.info("Successfully created all tables")
            return True
        except Error as e:
            logging.error(f"Error creating tables: {str(e)}")
            return False
    
    def insert_default_data(self):
        """Insert default data into the database."""
        try:
            cursor = self.conn.cursor()
            
            # Insert admin user
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password)
                VALUES (?, ?)
            ''', ('admin', 'admin123'))
            
            # Insert default menu categories
            categories = ['Beverages', 'Food', 'Desserts']
            for category in categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO menu_categories (name)
                    VALUES (?)
                ''', (category,))
            
            # Get category IDs
            cursor.execute('SELECT id, name FROM menu_categories')
            category_map = {name: id for id, name in cursor.fetchall()}
            
            # Insert default menu items
            menu_items = [
                ('Coffee', 'Beverages', 120.0),
                ('Tea', 'Beverages', 80.0),
                ('Sandwich', 'Food', 150.0),
                ('Pasta', 'Food', 200.0),
                ('Cake', 'Desserts', 180.0),
                ('Ice Cream', 'Desserts', 100.0)
            ]
            
            for name, category, price in menu_items:
                cursor.execute('''
                    INSERT OR IGNORE INTO menu_items (name, category_id, price)
                    VALUES (?, ?, ?)
                ''', (name, category_map[category], price))
            
            # Create 15 default tables
            for table_num in range(1, 16):
                cursor.execute('''
                    INSERT OR IGNORE INTO tables (table_number, status)
                    VALUES (?, 'vacant')
                ''', (table_num,))
            
            self.conn.commit()
            logging.info("Successfully inserted default data")
            return True
        except Error as e:
            logging.error(f"Error inserting default data: {str(e)}")
            return False
    
    def verify_tables(self):
        """Verify that all required tables exist."""
        try:
            cursor = self.conn.cursor()
            
            # Check all required tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    'sales', 'sale_items', 'menu_items', 
                    'menu_categories', 'expenses', 'bar_stock',
                    'staff', 'tables', 'users'
                )
            """)
            
            existing_tables = cursor.fetchall()
            print("Existing tables:", [table[0] for table in existing_tables])
            
            if len(existing_tables) < 9:
                print("Some tables are missing. Reinitializing database...")
                return False
            return True
            
        except Exception as e:
            print(f"Error verifying tables: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")
    
    def get_db_version(self):
        """Return the SQLite version."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT sqlite_version()')
            version = cursor.fetchone()[0]
            logging.info(f"Database version: {version}")
            return version
        except Error as e:
            logging.error(f"Error getting database version: {str(e)}")
            return None

def initialize_database():
    """Initialize the database with all tables and default data."""
    db_manager = DatabaseManager()
    
    if db_manager.connect():
        print("Successfully connected to database")
        
        # Verify tables first
        if not db_manager.verify_tables():
            if db_manager.create_tables():
                print("Successfully created tables")
                
                if db_manager.insert_default_data():
                    print("Successfully inserted default data")
                else:
                    print("Failed to insert default data")
            else:
                print("Failed to create tables")
        else:
            print("All required tables exist")
    else:
        print("Failed to connect to database")
    
    db_manager.close()

if __name__ == "__main__":
    initialize_database()
