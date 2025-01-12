"""
Database initialization script for the Cafe Management System.
Verifies and creates all required tables.
"""

from database import DatabaseManager, initialize_database
import sqlite3

def verify_and_create_tables():
    """Verify all required tables exist and create if missing"""
    try:
        db = DatabaseManager()
        conn = db.connect()
        cursor = conn.cursor()

        # Check existing tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table'
        """)
        
        existing_tables = [table[0] for table in cursor.fetchall()]
        print("Existing tables:", existing_tables)

        # List of required tables
        required_tables = [
            'users',
            'sales',
            'sale_items',
            'menu_items',
            'menu_categories',
            'tables',
            'expenses',
            'bar_stock',
            'stock_history',
            'staff',
            'staff_payments'
        ]

        # Check for missing tables
        missing_tables = [table for table in required_tables if table not in existing_tables]

        if missing_tables:
            print("Missing tables:", missing_tables)
            print("Initializing database...")
            initialize_database()
            print("Database initialized successfully!")
        else:
            print("All required tables exist!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_and_create_tables() 