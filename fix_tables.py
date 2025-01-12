"""
Script to fix database table creation order for Cafe Management System.
Creates tables in correct dependency order and adds default data.
"""

import sqlite3
import os

def create_tables_in_order():
    try:
        conn = sqlite3.connect('cafe_manager.db')
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 1. First create independent tables (no foreign keys)
        print("Creating base tables...")
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        
        # Tables table (needed by sales)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER UNIQUE NOT NULL,
            status TEXT CHECK(status IN ('vacant', 'occupied')) DEFAULT 'vacant',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Menu Categories (needed by menu_items)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')
        
        # 2. Then create tables with dependencies
        print("Creating dependent tables...")
        
        # Menu Items (depends on categories)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            FOREIGN KEY (category_id) REFERENCES menu_categories (id)
        )
        ''')
        
        # Sales (depends on tables)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            discount_type TEXT,
            discount_value REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            payment_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (table_number) REFERENCES tables (table_number)
        )
        ''')
        
        # Bar Stock (independent)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bar_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL,
            min_threshold INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Initialize default data
        print("Adding default data...")
        
        # Add default tables (1-15)
        for i in range(1, 16):
            cursor.execute('INSERT OR IGNORE INTO tables (table_number) VALUES (?)', (i,))
            
        # Add admin user
        cursor.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', 
                      ('admin', 'pass'))
        
        conn.commit()
        print("Database setup complete!")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nCreated tables:")
        for table in tables:
            print(f"- {table[0]}")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database setup...")
    create_tables_in_order() 