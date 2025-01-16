import sqlite3
import os

def clear_data():
    try:
        # Connect to the database
        conn = sqlite3.connect('cafe_manager.db')
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        print("Starting data cleanup...")
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            # Clear sales related data (order matters due to foreign keys)
            cursor.execute("DELETE FROM sale_items")
            cursor.execute("DELETE FROM sales")
            cursor.execute("DELETE FROM temporary_bills")
            print("✓ Cleared sales data")
            
            # Clear expenses
            cursor.execute("DELETE FROM expenses")
            print("✓ Cleared expenses data")
            
            # Clear stock related data
            cursor.execute("DELETE FROM stock_history")
            cursor.execute("DELETE FROM bar_stock")
            print("✓ Cleared stock data")
            
            # Reset all tables to vacant status
            cursor.execute("UPDATE tables SET status = 'vacant'")
            print("✓ Reset table statuses")
            
            # Commit the transaction
            conn.commit()
            print("\nAll data cleared successfully!")
            
        except Exception as e:
            # If any error occurs, rollback the transaction
            conn.rollback()
            print(f"Error occurred: {str(e)}")
            print("No changes were made to the database")
            
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clear_data() 