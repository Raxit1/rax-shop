# setup_pythonanywhere.py
import sqlite3
import os

def setup_database():
    """Setup database with initial admin user and sample data"""
    
    # Use a persistent path on PythonAnywhere
    # Change 'yourusername' to your actual PythonAnywhere username
    db_path = '/home/yourusername/rax-shop/users.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT,
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            product_category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
    ''')
    
    # Create admin user
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, password, email, is_admin)
            VALUES ('admin', 'admin123', 'admin@example.com', 1)
        """)
        print("✅ Admin user created - Username: admin, Password: admin123")
    
    # Add sample products
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ('The Great Gatsby', 'books', 12.99, 'Classic novel', 'book1.jpg', 50),
            ('Python Programming', 'books', 29.99, 'Learn Python', 'book2.jpg', 30),
            ('Smartphone X', 'electronics', 599.99, 'Latest smartphone', 'phone.jpg', 20),
            ('Laptop Pro', 'electronics', 999.99, 'High performance laptop', 'laptop.jpg', 15),
            ("Men's Shirt", 'fashion', 29.99, 'Cotton shirt', 'shirt.jpg', 100),
            ("Women's Dress", 'fashion', 49.99, 'Elegant dress', 'dress.jpg', 75),
            ('Organic Apples', 'grocery', 4.99, 'Fresh organic apples', 'apples.jpg', 200),
            ('Whole Wheat Bread', 'grocery', 2.99, 'Healthy bread', 'bread.jpg', 150)
        ]
        
        cursor.executemany("""
            INSERT INTO products (name, category, price, description, image, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, products)
        print("✅ Sample products added")
    
    conn.commit()
    conn.close()
    print(f"✅ Database setup complete at: {db_path}")

if __name__ == '__main__':
    setup_database()