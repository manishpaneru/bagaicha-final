"""
Database setup script for Cafe Management System.
Creates all necessary tables and inserts default data.
"""

import sqlite3
import os
from pathlib import Path

def setup_database():
    # Remove existing database if it exists
    if os.path.exists('cafe_manager.db'):
        os.remove('cafe_manager.db')
    
    print("Creating new database...")
    conn = sqlite3.connect('cafe_manager.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    print("\nCreating tables...")
    
    # 1. Menu Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)
    
    # 2. Menu Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (category_id) REFERENCES menu_categories (id)
    )
    """)
    
    # 3. Sales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_number INTEGER NOT NULL,
        subtotal REAL NOT NULL,
        discount_type TEXT,
        discount_value REAL,
        total_amount REAL NOT NULL,
        payment_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (table_number) REFERENCES tables (table_number)
    )
    """)
    
    # 4. Sale Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        menu_item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        total_price REAL NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
        FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
    )
    """)
    
    # 5. Bar Stock
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bar_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL UNIQUE,
        quantity INTEGER NOT NULL,
        min_threshold INTEGER NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 6. Stock History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        change_quantity REAL NOT NULL,
        operation_type TEXT CHECK(operation_type IN ('add', 'remove')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES bar_stock (id)
    )
    """)
    
    # 7. Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_number INTEGER UNIQUE NOT NULL,
        status TEXT CHECK(status IN ('vacant', 'occupied')) DEFAULT 'vacant',
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 8. Staff
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        title TEXT NOT NULL,
        contact TEXT NOT NULL,
        salary REAL NOT NULL,
        join_date DATE NOT NULL,
        last_paid_date DATE,
        is_active BOOLEAN DEFAULT 1
    )
    """)
    
    # 9. Staff Payments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_date DATE NOT NULL,
        FOREIGN KEY (staff_id) REFERENCES staff (id)
    )
    """)
    
    # 10. Expenses
    cursor.execute("""
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
    """)
    
    # 11. Users (Admin)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    
    print("\nInserting default data...")
    
    # Insert default admin user
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password)
    VALUES (?, ?)
    """, ('admin', 'admin123'))
    
    # Insert default tables (1-15)
    for table_num in range(1, 16):
        cursor.execute("""
        INSERT OR IGNORE INTO tables (table_number)
        VALUES (?)
        """, (table_num,))
    
    # Insert default menu categories
    categories = ['Beverages', 'Food', 'Desserts']
    for category in categories:
        cursor.execute("""
        INSERT OR IGNORE INTO menu_categories (name)
        VALUES (?)
        """, (category,))
    
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
        cursor.execute("""
        INSERT OR IGNORE INTO menu_items (name, category_id, price)
        VALUES (?, ?, ?)
        """, (name, category_map[category], price))
    
    # Commit all changes
    conn.commit()
    
    print("\nVerifying tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [table[0] for table in cursor.fetchall()]
    print("Existing tables:", existing_tables)
    
    conn.close()
    print("\nDatabase setup complete!")

if __name__ == "__main__":
    setup_database() 