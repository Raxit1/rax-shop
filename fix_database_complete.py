import sqlite3
from datetime import datetime

def fix_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    print("=" * 50)
    print("Fixing Database Schema")
    print("=" * 50)
    print(f"Current columns: {columns}")
    
    # Add is_admin column if missing
    if 'is_admin' not in columns:
        print("\n📌 Adding is_admin column...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        print("✓ is_admin column added")
    
    # Add created_at column if missing
    if 'created_at' not in columns:
        print("\n📌 Adding created_at column...")
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
        
        # Set default date for existing users
        default_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE users SET created_at = ? WHERE created_at IS NULL", (default_date,))
        print("✓ created_at column added and populated")
    
    # Verify all columns now exist
    cursor.execute("PRAGMA table_info(users)")
    updated_columns = [column[1] for column in cursor.fetchall()]
    print(f"\n✅ Updated columns: {updated_columns}")
    
    # Show user count
    user_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    admin_count = cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1").fetchone()[0]
    
    print(f"\n📊 Database Statistics:")
    print(f"   Total users: {user_count}")
    print(f"   Admin users: {admin_count}")
    print(f"   Regular users: {user_count - admin_count}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database fix completed successfully!")

if __name__ == "__main__":
    fix_database()