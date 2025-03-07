"""
Database initialization script for the Cafe Management System.
Creates and initializes all required tables with proper relationships.
"""

import sqlite3
import os

def initialize_database():
    # Connect to database (creates it if it doesn't exist)
    conn = sqlite3.connect('cafe_manager.db')
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create menu_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Create menu_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category_id INTEGER,
                price REAL NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES menu_categories(id)
            )
        ''')
        
        # Create tables table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY,
                table_number INTEGER UNIQUE NOT NULL,
                status TEXT CHECK(status IN ('vacant', 'occupied')) DEFAULT 'vacant',
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                table_number INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                discount_type TEXT CHECK(discount_type IN ('percentage', 'amount')),
                discount_value REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                payment_status TEXT CHECK(payment_status IN ('pending', 'completed')) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_number) REFERENCES tables(table_number)
            )
        ''')
        
        # Create sale_items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY,
                sale_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit REAL NOT NULL,
                total_price REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
            )
        ''')
        
        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit REAL NOT NULL,
                total_price REAL NOT NULL,
                expense_date DATE DEFAULT CURRENT_DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create staff table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                contact TEXT NOT NULL,
                salary REAL NOT NULL,
                join_date DATE NOT NULL,
                last_paid_date DATE,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create staff_payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff_payments (
                id INTEGER PRIMARY KEY,
                staff_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (staff_id) REFERENCES staff(id)
            )
        ''')
        
        # Create bar_stock table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bar_stock (
                id INTEGER PRIMARY KEY,
                item_name TEXT NOT NULL UNIQUE,
                quantity INTEGER NOT NULL,
                min_threshold INTEGER NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create stock_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY,
                item_id INTEGER NOT NULL,
                change_quantity INTEGER NOT NULL,
                operation_type TEXT CHECK(operation_type IN ('add', 'remove')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES bar_stock(id)
            )
        ''')
        
        # Insert default data
        
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
        
        # Insert default tables
        for i in range(1, 16):
            cursor.execute('''
                INSERT OR IGNORE INTO tables (table_number)
                VALUES (?)
            ''', (i,))
        
        # Commit changes
        conn.commit()
        print("Database initialized successfully!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def check_tables():
    """Verify all required tables exist"""
    conn = sqlite3.connect('cafe_manager.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\nExisting tables:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()

if __name__ == "__main__":
    initialize_database()
    check_tables() 