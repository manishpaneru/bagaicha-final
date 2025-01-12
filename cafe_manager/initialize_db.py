"""
Database initialization script for the Cafe Management System.
Creates all required tables and inserts default data.
"""

import os
from database import DatabaseManager

def initialize_database():
    """Initialize the database with all tables and default data."""
    # Get database path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, 'cafe_manager.db')
    
    # Delete existing database if it exists
    if os.path.exists(db_path):
        print(f"Removing existing database at: {db_path}")
        os.remove(db_path)
    
    # Create new database
    db_manager = DatabaseManager()
    
    # Connect and initialize
    if db_manager.connect():
        print("Successfully connected to database")
        
        if db_manager.create_tables():
            print("Successfully created tables")
            
            if db_manager.insert_default_data():
                print("Successfully inserted default data")
            else:
                print("Failed to insert default data")
        else:
            print("Failed to create tables")
    else:
        print("Failed to connect to database")
    
    db_manager.close()

if __name__ == "__main__":
    initialize_database() 