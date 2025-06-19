import sqlite3
import os

def test_sqlite():
    print("Testing SQLite3...")
    
    # Test SQLite3 is available
    print(f"SQLite3 version: {sqlite3.sqlite_version}")
    print(f"Python SQLite3 module version: {sqlite3.version}")
    
    # Test database creation
    db_path = "./data/test.db"
    os.makedirs("data", exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create a test table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test_entry",))
        conn.commit()
        
        # Query test data
        cursor.execute("SELECT * FROM test_table")
        results = cursor.fetchall()
        print(f"Test data retrieved: {results}")
        
        conn.close()
        print("✅ SQLite3 is working perfectly!")
        
        # Clean up test file
        os.remove(db_path)
        
    except Exception as e:
        print(f"❌ SQLite3 test failed: {e}")

if __name__ == "__main__":
    test_sqlite()