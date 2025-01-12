"""
Database setup script for the Cafe Management System.
Creates and initializes all required tables with proper relationships.
"""

import sqlite3
from pathlib import Path

def setup_database():
    """Create and initialize all database tables"""
    # Create database file in the correct location
    db_path = Path("cafe_manager.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("Setting up database tables...")
        
        # Create all required tables
        
        # 1. Sales table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            discount_type TEXT CHECK(discount_type IN ('percentage', 'amount')),
            discount_value REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            payment_status TEXT CHECK(payment_status IN ('pending', 'completed')) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 2. Menu Categories
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """)
        
        # 3. Menu Items
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES menu_categories (id)
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
        print("Database setup completed successfully!")
        
        # Verify tables were created
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
    setup_database() 