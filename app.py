from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import random
import string

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("users.db")

# Create tables with admin support
conn = get_db()

# Users table with admin column
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    MobileNo TEXT,
    password TEXT,
    is_admin INTEGER DEFAULT 0
)
""")

# Orders table for tracking shipped items
conn.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    order_id TEXT UNIQUE,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    postal_code TEXT,
    payment_method TEXT,
    notes TEXT,
    total_amount REAL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Processing',
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# Order items table
conn.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    product_name TEXT,
    product_category TEXT,
    quantity INTEGER,
    price REAL,
    subtotal REAL,
    FOREIGN KEY(order_id) REFERENCES orders(order_id)
)
""")

# Shipping/Delivery table
conn.execute("""
CREATE TABLE IF NOT EXISTS shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT UNIQUE,
    tracking_number TEXT,
    shipped_date TIMESTAMP,
    estimated_delivery DATE,
    current_location TEXT,
    status TEXT DEFAULT 'Order Placed',
    notes TEXT,
    FOREIGN KEY(order_id) REFERENCES orders(order_id)
)
""")

# Products table for admin to manage
conn.execute("""
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

# Order status history table
conn.execute("""
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

conn.commit()
conn.close()

# ==================== CUSTOMER ROUTES ====================

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register_user", methods=["POST"])
def register_user():
    username = request.form["username"]
    email = request.form["email"]
    MobileNo = request.form["MobileNo"]
    password = generate_password_hash(request.form["password"])
    
    conn = get_db()
    
    # Check if user already exists
    existing = conn.execute(
        "SELECT * FROM users WHERE email = ? OR username = ?",
        (email, username)
    ).fetchone()
    
    if existing:
        conn.close()
        return "User already exists! Please login."
    
    # Regular users have is_admin = 0 by default
    conn.execute(
        "INSERT INTO users (username, email, MobileNo, password, is_admin) VALUES (?, ?, ?, ?, 0)",
        (username, email, MobileNo, password)
    )
    conn.commit()
    conn.close()
    
    return redirect("/")

@app.route("/login_user", methods=["POST"])
def login_user():
    email_or_mobile = request.form["email"]
    password = request.form["password"]
    
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? OR MobileNo = ?",
        (email_or_mobile, email_or_mobile)
    ).fetchone()
    conn.close()
    
    if user and check_password_hash(user[4], password):
        # Check if user is admin - if yes, redirect to admin panel
        if user[5] == 1:  # is_admin = 1
            session["admin"] = user[1]
            session["admin_id"] = user[0]
            return redirect("/admin/dashboard")
        else:
            session["user"] = user[1]
            return redirect("/dashboard")
    else:
        return "Invalid Login Credentials"

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect("/")

@app.route("/electronics")
def electronics():
    if "user" not in session:
        return redirect("/")
    return render_template("electronics.html", user=session["user"])

@app.route("/books")
def books():
    if "user" not in session:
        return redirect("/")
    return render_template("books.html", user=session["user"])

@app.route("/grocery")
def grocery():
    if "user" not in session:
        return redirect("/")
    return render_template("grocery.html", user=session["user"])

@app.route("/fashion")
def fashion():
    if "user" not in session:
        return redirect("/")
    return render_template("fashion.html", user=session["user"])

@app.route("/cart")
def cart():
    if "user" not in session:
        return redirect("/")
    cart_items = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart_items)
    return render_template("cart.html", user=session["user"], cart_items=cart_items, total=total)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user" not in session:
        return jsonify({"error": "Please login first"}), 401
    
    data = request.get_json()
    item = {
        "id": data["id"],
        "name": data["name"],
        "price": data["price"],
        "quantity": data.get("quantity", 1),
        "category": data["category"]
    }
    
    if "cart" not in session:
        session["cart"] = []
    
    # Check if item already in cart
    for cart_item in session["cart"]:
        if cart_item["id"] == item["id"]:
            cart_item["quantity"] += item["quantity"]
            session.modified = True
            return jsonify({"success": True, "message": "Item quantity updated"})
    
    session["cart"].append(item)
    session.modified = True
    return jsonify({"success": True, "message": "Item added to cart"})

@app.route("/remove_from_cart/<item_id>", methods=["POST"])
def remove_from_cart(item_id):
    if "user" not in session:
        return redirect("/")
    
    if "cart" in session:
        session["cart"] = [item for item in session["cart"] if item["id"] != item_id]
        session.modified = True
    return redirect("/cart")

@app.route("/update_quantity/<item_id>/<int:quantity>", methods=["POST"])
def update_quantity(item_id, quantity):
    if "user" not in session:
        return redirect("/")
    
    if "cart" in session:
        for item in session["cart"]:
            if item["id"] == item_id:
                item["quantity"] = max(1, quantity)
                break
        session.modified = True
    return redirect("/cart")

@app.route("/checkout")
def checkout():
    if "user" not in session:
        return redirect("/")
    cart_items = session.get("cart", [])
    if not cart_items:
        return redirect("/cart")
    total = sum(item["price"] * item["quantity"] for item in cart_items)
    return render_template("checkout.html", user=session["user"], cart_items=cart_items, total=total)

@app.route("/place_order", methods=["POST"])
def place_order():
    if "user" not in session or "cart" not in session or not session["cart"]:
        return redirect("/")
    
    # Generate Order ID
    order_id = "ORD-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    tracking_number = "TRK-" + ''.join(random.choices(string.digits, k=12))
    
    # Get form data
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    city = request.form.get("city")
    postal_code = request.form.get("postal_code")
    payment_method = request.form.get("payment_method")
    notes = request.form.get("notes", "")
    
    # Calculate total
    cart_items = session["cart"]
    total = sum(item["price"] * item["quantity"] for item in cart_items)
    total_with_tax = total * 1.1
    
    try:
        conn = get_db()
        
        # Get user ID
        user_data = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (session["user"],)
        ).fetchone()
        user_id = user_data[0] if user_data else None
        
        # Insert order
        conn.execute("""
            INSERT INTO orders (user_id, order_id, full_name, email, phone, address, city, postal_code, payment_method, notes, total_amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Processing')
        """, (user_id, order_id, full_name, email, phone, address, city, postal_code, payment_method, notes, total_with_tax))
        
        # Insert order items
        for item in cart_items:
            conn.execute("""
                INSERT INTO order_items (order_id, product_name, product_category, quantity, price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_id, item["name"], item["category"], item["quantity"], item["price"], item["price"] * item["quantity"]))
        
        # Insert shipment record
        estimated_delivery = (datetime.datetime.now() + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
        conn.execute("""
            INSERT INTO shipments (order_id, tracking_number, estimated_delivery, current_location, status)
            VALUES (?, ?, ?, 'Warehouse', 'Order Placed')
        """, (order_id, tracking_number, estimated_delivery))
        
        conn.commit()
        conn.close()
        
        # Clear cart from session
        order_items = session["cart"].copy()
        session.pop("cart", None)
        session.modified = True
        
        return render_template("order_success.html", user=session["user"], order_items=order_items, order_id=order_id, tracking_number=tracking_number, total=total_with_tax)
        
    except Exception as e:
        print(f"Error placing order: {e}")
        return "Error placing order", 500

@app.route("/orders")
def orders():
    if "user" not in session:
        return redirect("/")
    
    try:
        conn = get_db()
        user_data = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (session["user"],)
        ).fetchone()
        
        if not user_data:
            return redirect("/")
        
        user_id = user_data[0]
        
        # Get all orders for user
        orders_data = conn.execute("""
            SELECT o.order_id, o.full_name, o.total_amount, o.order_date, o.status, 
                   s.tracking_number, s.current_location, s.estimated_delivery
            FROM orders o
            LEFT JOIN shipments s ON o.order_id = s.order_id
            WHERE o.user_id = ?
            ORDER BY o.order_date DESC
        """, (user_id,)).fetchall()
        
        conn.close()
        
        return render_template("orders.html", user=session["user"], orders=orders_data)
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return redirect("/dashboard")

@app.route("/track_order/<order_id>")
def track_order(order_id):
    if "user" not in session:
        return redirect("/")
    
    try:
        conn = get_db()
        
        # Get order details
        order = conn.execute("""
            SELECT o.*, s.tracking_number, s.shipped_date, s.current_location, s.status as shipment_status, s.estimated_delivery
            FROM orders o
            LEFT JOIN shipments s ON o.order_id = s.order_id
            WHERE o.order_id = ?
        """, (order_id,)).fetchone()
        
        # Get order items
        items = conn.execute("""
            SELECT product_name, product_category, quantity, price, subtotal
            FROM order_items
            WHERE order_id = ?
        """, (order_id,)).fetchall()
        
        conn.close()
        
        if order:
            return render_template("track_order.html", user=session["user"], order=order, items=items)
        else:
            return redirect("/orders")
    except Exception as e:
        print(f"Error tracking order: {e}")
        return redirect("/orders")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("cart", None)
    return redirect("/")

# ==================== ADMIN ROUTES ====================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE (email = ? OR username = ?) AND is_admin = 1",
            (username, username)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user[4], password):
            session["admin"] = user[1]
            session["admin_id"] = user[0]
            return redirect("/admin/dashboard")
        else:
            return render_template("admin_login.html", error="Invalid admin credentials")
    
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin/login")
    
    conn = get_db()
    
    # Get statistics
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_revenue = conn.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders").fetchone()[0]
    total_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0").fetchone()[0]
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    
    # Get recent orders
    recent_orders = conn.execute("""
        SELECT o.order_id, o.full_name, o.total_amount, o.status, o.order_date
        FROM orders o
        ORDER BY o.order_date DESC
        LIMIT 10
    """).fetchall()
    
    conn.close()
    
    return render_template("admin_dashboard.html", 
                         admin_name=session["admin"],
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         total_users=total_users,
                         total_products=total_products,
                         recent_orders=recent_orders)

@app.route("/admin/orders")
def admin_orders():
    if "admin" not in session:
        return redirect("/admin/login")
    
    conn = get_db()
    orders = conn.execute("""
        SELECT o.order_id, o.full_name, o.email, o.total_amount, o.status, o.order_date,
               s.tracking_number, s.current_location
        FROM orders o
        LEFT JOIN shipments s ON o.order_id = s.order_id
        ORDER BY o.order_date DESC
    """).fetchall()
    conn.close()
    
    return render_template("admin_orders.html", admin_name=session["admin"], orders=orders)

@app.route("/admin/orders/<order_id>")
def admin_order_detail(order_id):
    if "admin" not in session:
        return redirect("/admin/login")
    
    conn = get_db()
    
    order = conn.execute("""
        SELECT o.*, s.tracking_number, s.shipped_date, s.current_location, s.status as shipment_status, s.estimated_delivery
        FROM orders o
        LEFT JOIN shipments s ON o.order_id = s.order_id
        WHERE o.order_id = ?
    """, (order_id,)).fetchone()
    
    items = conn.execute("""
        SELECT product_name, quantity, price, subtotal
        FROM order_items
        WHERE order_id = ?
    """, (order_id,)).fetchall()
    
    # Get status history
    status_history = conn.execute("""
        SELECT status, updated_by, updated_at, notes
        FROM order_status_history
        WHERE order_id = ?
        ORDER BY updated_at DESC
    """, (order_id,)).fetchall()
    
    conn.close()
    
    return render_template("admin_order_detail.html", 
                         admin_name=session["admin"], 
                         order=order, 
                         items=items,
                         status_history=status_history)

@app.route("/admin/update_order_status", methods=["POST"])
def update_order_status():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    order_id = data.get("order_id")
    new_status = data.get("status")
    
    if not order_id or not new_status:
        return jsonify({"error": "Missing data"}), 400
    
    conn = get_db()
    
    # Update order status
    conn.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?",
        (new_status, order_id)
    )
    
    # Update shipment status if applicable
    if new_status in ["Shipped", "Delivered"]:
        conn.execute(
            "UPDATE shipments SET status = ? WHERE order_id = ?",
            (new_status, order_id)
        )
        
        if new_status == "Shipped" and not conn.execute("SELECT shipped_date FROM shipments WHERE order_id = ?", (order_id,)).fetchone()[0]:
            conn.execute(
                "UPDATE shipments SET shipped_date = CURRENT_TIMESTAMP WHERE order_id = ?",
                (order_id,)
            )
    
    # Log status change
    conn.execute("""
        INSERT INTO order_status_history (order_id, status, updated_by, notes)
        VALUES (?, ?, ?, ?)
    """, (order_id, new_status, session["admin"], f"Status updated to {new_status} by admin"))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Order status updated"})

@app.route("/admin/products")
def admin_products():
    if "admin" not in session:
        return redirect("/admin/login")
    
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY created_at DESC").fetchall()
    conn.close()
    
    return render_template("admin_products.html", admin_name=session["admin"], products=products)

@app.route("/admin/add_product", methods=["POST"])
def add_product():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    
    # Generate product ID if not provided
    if not data.get("product_id"):
        data["product_id"] = "PROD-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    conn = get_db()
    
    try:
        conn.execute("""
            INSERT INTO products (product_id, name, category, price, description, image_url, stock, rating, features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (data["product_id"], data["name"], data["category"], data["price"], 
              data.get("description", ""), data.get("image_url", ""), 
              data.get("stock", 0), data.get("rating", 0), 
              data.get("features", "")))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "product_id": data["product_id"]})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route("/admin/update_product/<product_id>", methods=["POST"])
def update_product(product_id):
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    conn = get_db()
    
    try:
        conn.execute("""
            UPDATE products 
            SET name = ?, category = ?, price = ?, description = ?, image_url = ?, stock = ?, rating = ?, features = ?
            WHERE product_id = ?
        """, (data["name"], data["category"], data["price"], data.get("description", ""),
              data.get("image_url", ""), data.get("stock", 0), data.get("rating", 0),
              data.get("features", ""), product_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route("/admin/delete_product/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db()
    
    try:
        conn.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route("/admin/users")
def admin_users():
    if "admin" not in session:
        return redirect("/admin/login")
    
    conn = get_db()
    
    # Check if created_at column exists
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # If created_at exists, include it, otherwise don't
    if 'created_at' in columns:
        users = conn.execute("SELECT id, username, email, MobileNo, is_admin, created_at FROM users ORDER BY id DESC").fetchall()
    else:
        users = conn.execute("SELECT id, username, email, MobileNo, is_admin FROM users ORDER BY id DESC").fetchall()
    
    conn.close()
    
    return render_template("admin_users.html", admin_name=session["admin"], users=users)

@app.route("/admin/update_user_status", methods=["POST"])
def update_user_status():
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user_id = data.get("user_id")
    is_admin = data.get("is_admin", 0)
    
    conn = get_db()
    conn.execute("UPDATE users SET is_admin = ? WHERE id = ?", (is_admin, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})
@app.route("/admin/get_product/<product_id>")
def admin_get_product(product_id):
    if "admin" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE product_id = ?", (product_id,)).fetchone()
    conn.close()
    
    if product:
        return jsonify({
            "success": True,
            "product": {
                "product_id": product[1],
                "name": product[2],
                "category": product[3],
                "price": product[4],
                "description": product[5],
                "image_url": product[6],
                "stock": product[7],
                "rating": product[8],
                "features": product[9]
            }
        })
    else:
        return jsonify({"success": False, "error": "Product not found"}), 404

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect("/admin/login")

# ==================== SAMPLE PRODUCT DATA (Optional) ====================

@app.route("/admin/seed_products")
def seed_products():
    """Optional: Add sample products to database"""
    if "admin" not in session:
        return "Unauthorized", 401
    
    sample_products = [
        ("PROD-ELEC-001", "Smartphone X", "Electronics", 599.99, "Latest flagship smartphone", "https://images.unsplash.com/photo-1511707267537-b85faf00021e", 50, 4.8, "6.7 inch Display,5G,12MP Camera"),
        ("PROD-ELEC-002", "Laptop Pro", "Electronics", 1299.99, "High-performance laptop", "https://images.unsplash.com/photo-1588872657840-790ff3bda791", 30, 4.9, "Intel i7,16GB RAM,512GB SSD"),
        ("PROD-BOOK-001", "The Great Novel", "Books", 24.99, "Best selling fiction novel", "https://www.crossword.in/cdn/shop/files/81Lfw-skUsL._SL1500.jpg", 100, 4.8, "Hardcover,450 Pages,Bestseller"),
        ("PROD-BOOK-002", "Python Programming", "Books", 34.99, "Learn Python programming", "https://www.wileyindia.com/pub/media/catalog/product/cache/20f980a1f90e8cec7a3c8f2cf40a32a8/9/7/9789357465304_1.jpg", 75, 4.9, "Technical,600 Pages,Code Examples"),
    ]
    
    conn = get_db()
    for product in sample_products:
        try:
            conn.execute("""
                INSERT INTO products (product_id, name, category, price, description, image_url, stock, rating, features)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, product)
        except sqlite3.IntegrityError:
            pass  # Product already exists
    
    conn.commit()
    conn.close()
    
    return "Sample products added successfully!"

# Add this at the very bottom of app.py
app = app

if __name__ == "__main__":
    app.run()