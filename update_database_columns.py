import sqlite3

def update_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Check and add missing columns to users table
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    print("Current columns in users table:", columns)
    
    # Add created_at column if not exists
    if 'created_at' not in columns:
        print("Adding created_at column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("✓ created_at column added")
    else:
        print("created_at column already exists")
    
    # Add any other missing columns
    if 'is_admin' not in columns:
        print("Adding is_admin column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        print("✓ is_admin column added")
    
    # Check if users table has all required columns
    cursor.execute("SELECT * FROM users LIMIT 1")
    sample = cursor.fetchone()
    if sample:
        print(f"\nUsers table has {len(sample)} columns")
    
    conn.commit()
    conn.close()
    print("\n✅ Database update completed successfully!")

if __name__ == "__main__":
    update_database()