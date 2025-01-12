import sqlite3

def test_database():
    try:
        conn = sqlite3.connect('cafe_manager.db')
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute('SELECT * FROM users')
        print('Users:', cursor.fetchall())
        
        # Check tables
        cursor.execute('SELECT COUNT(*) FROM tables WHERE status = ?', ('vacant',))
        print('Number of vacant tables:', cursor.fetchone()[0])
        
        conn.close()
        print('Database test completed successfully')
        
    except sqlite3.Error as e:
        print(f'Database error: {str(e)}')
        
if __name__ == '__main__':
    test_database() 