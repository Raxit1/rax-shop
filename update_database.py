import sqlite3

def update_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Check if is_admin column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_admin' not in columns:
        print("Adding is_admin column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        print("✓ is_admin column added")
    else:
        print("is_admin column already exists")
    
    # Create products table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT UNIQUE,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        image_url TEXT,
        stock INTEGER DEFAULT 0,
        rating REAL DEFAULT 0,
        features TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("✓ products table ready")
    
    # Create order_status_history table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id TEXT,
        status TEXT,
        updated_by TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY(order_id) REFERENCES orders(order_id)
    )
    """)
    print("✓ order_status_history table ready")
    
    conn.commit()
    conn.close()
    print("\nDatabase update completed successfully!")

if __name__ == "__main__":
    update_database()