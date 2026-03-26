import sqlite3
from werkzeug.security import generate_password_hash

def setup_admin():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # First check if is_admin column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_admin' not in columns:
        print("Database needs update. Run update_database.py first!")
        conn.close()
        return
    
    # Check if any admin exists
    cursor.execute("SELECT * FROM users WHERE is_admin = 1")
    admin = cursor.fetchone()
    
    if not admin:
        print("=" * 50)
        print("No admin user found. Let's create one!")
        print("=" * 50)
        
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
        
        if not username or not email or not password:
            print("All fields are required!")
            conn.close()
            return
        
        hashed_password = generate_password_hash(password)
        
        try:
            cursor.execute("""
                INSERT INTO users (username, email, MobileNo, password, is_admin)
                VALUES (?, ?, ?, ?, 1)
            """, (username, email, "0000000000", hashed_password))
            
            conn.commit()
            print("\n✓ Admin user created successfully!")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            print("  You can now login at: http://localhost:5000/admin/login")
            
        except sqlite3.IntegrityError:
            print("\n✗ Error: Username or email already exists!")
            
    else:
        print(f"Admin user already exists: {admin[1]} (ID: {admin[0]})")
        print("You can login with existing admin credentials")
    
    conn.close()

if __name__ == "__main__":
    setup_admin()