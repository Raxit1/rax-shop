from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("users.db")

# Create tables
conn = get_db()

# Users table
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    MobileNo TEXT,
    password TEXT
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

conn.commit()
conn.close()

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
    conn.execute(
        "INSERT INTO users (username, email, MobileNo, password) VALUES (?, ?, ?, ?)",
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
        session["user"] = user[1]
        return redirect("/dashboard")
    else:
        return "Invalid Login Make Sure"
    
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
            return {"success": True, "message": "Item quantity updated"}
    
    session["cart"].append(item)
    session.modified = True
    return {"success": True, "message": "Item added to cart"}
@app.route("/remove_from_cart/<item_id>", methods=["POST"])
def remove_from_cart(item_id):
    if "cart" in session:
        session["cart"] = [item for item in session["cart"] if item["id"] != item_id]
        session.modified = True
    return redirect("/cart")

@app.route("/update_quantity/<item_id>/<int:quantity>", methods=["POST"])
def update_quantity(item_id, quantity):
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
    
    import datetime
    import random
    import string
    
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
        return render_template("order_success.html", user=session["user"], order_items=order_items, order_id=order_id)

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
            SELECT o.*, s.tracking_number, s.shipped_date, s.current_location, s.status, s.estimated_delivery
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


