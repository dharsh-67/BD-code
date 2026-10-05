from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = "bakery.db"


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def create_tables():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT UNIQUE,
            address TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            description TEXT,
            price REAL,
            availability INTEGER DEFAULT 1
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            flavor TEXT,
            size TEXT,
            delivery_type TEXT,
            delivery_address TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    db.commit()
    db.close()


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json

    db = get_db()

    try:
        cursor = db.execute("""
            INSERT INTO users(name, phone, email, address)
            VALUES (?, ?, ?, ?)
        """, (
            data["name"],
            data["phone"],
            data["email"],
            data["address"]
        ))

        db.commit()
        return jsonify({
            "message": "User created",
            "user_id": cursor.lastrowid
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        db.close()


@app.route("/users", methods=["GET"])
def get_users():
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    db.close()

    return jsonify([dict(user) for user in users])


@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (id,)
    ).fetchone()
    db.close()

    if user:
        return jsonify(dict(user))

    return jsonify({"error": "User not found"}), 404


@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    data = request.json

    db = get_db()

    cursor = db.execute("""
        UPDATE users
        SET name=?, phone=?, email=?, address=?
        WHERE id=?
    """, (
        data["name"],
        data["phone"],
        data["email"],
        data["address"],
        id
    ))

    db.commit()
    db.close()

    if cursor.rowcount:
        return jsonify({"message": "User updated"})

    return jsonify({"error": "User not found"}), 404


@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    db = get_db()

    cursor = db.execute(
        "DELETE FROM users WHERE id=?", (id,)
    )

    db.commit()
    db.close()

    if cursor.rowcount:
        return jsonify({"message": "User deleted"})

    return jsonify({"error": "User not found"}), 404


@app.route("/products", methods=["POST"])
def create_product():
    data = request.json

    db = get_db()

    cursor = db.execute("""
        INSERT INTO products
        (name, category, description, price, availability)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["category"],
        data["description"],
        data["price"],
        data.get("availability", 1)
    ))

    db.commit()

    product_id = cursor.lastrowid
    db.close()

    return jsonify({
        "message": "Product created",
        "product_id": product_id
    })


@app.route("/products", methods=["GET"])
def get_products():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    db.close()

    return jsonify([dict(product) for product in products])


@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    db = get_db()

    product = db.execute(
        "SELECT * FROM products WHERE id=?", (id,)
    ).fetchone()

    db.close()

    if product:
        return jsonify(dict(product))

    return jsonify({"error": "Product not found"}), 404


@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    data = request.json

    db = get_db()

    cursor = db.execute("""
        UPDATE products
        SET name=?, category=?, description=?,
            price=?, availability=?
        WHERE id=?
    """, (
        data["name"],
        data["category"],
        data["description"],
        data["price"],
        data["availability"],
        id
    ))

    db.commit()
    db.close()

    if cursor.rowcount:
        return jsonify({"message": "Product updated"})

    return jsonify({"error": "Product not found"}), 404


@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    db = get_db()

    cursor = db.execute(
        "DELETE FROM products WHERE id=?", (id,)
    )

    db.commit()
    db.close()

    if cursor.rowcount:
        return jsonify({"message": "Product deleted"})

    return jsonify({"error": "Product not found"}), 404


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json

    db = get_db()

    cursor = db.execute("""
        INSERT INTO orders
        (user_id, product_id, quantity, flavor, size,
         delivery_type, delivery_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["user_id"],
        data["product_id"],
        data["quantity"],
        data["flavor"],
        data["size"],
        data["delivery_type"],
        data["delivery_address"]
    ))

    db.commit()

    order_id = cursor.lastrowid
    db.close()

    return jsonify({
        "message": "Order placed",
        "order_id": order_id
    })


@app.route("/orders", methods=["GET"])
def get_orders():
    db = get_db()

    orders = db.execute("""
        SELECT orders.id,
               users.name AS customer,
               products.name AS product,
               orders.quantity,
               orders.flavor,
               orders.size,
               orders.delivery_type,
               orders.delivery_address,
               orders.status
        FROM orders
        JOIN users ON orders.user_id = users.id
        JOIN products ON orders.product_id = products.id
    """).fetchall()

    db.close()

    return jsonify([dict(order) for order in orders])


@app.route("/orders/<int:id>", methods=["GET"])
def get_order(id):
    db = get_db()

    order = db.execute("""
        SELECT orders.*,
               users.name AS customer,
               products.name AS product
        FROM orders
        JOIN users ON orders.user_id = users.id
        JOIN products ON orders.product_id = products.id
        WHERE orders.id=?
    """, (id,)).fetchone()

    db.close()

    if order:
        return jsonify(dict(order))

    return jsonify({"error": "Order not found"}), 404


@app.route("/orders/<int:id>", methods=["PUT"])
def update_order(id):
    data = request.json

    db = get_db()

    cursor = db.execute("""
        UPDATE orders
        SET status=?, delivery_address=?
        WHERE id=?
    """, (
        data["status"],
        data["delivery_address"],
        id
    ))

    db.commit()
    db.close()

    if cursor.rowcount:
        return jsonify({"message": "Order updated"})

    return jsonify({"error": "Order not found"}), 404


@app.route("/orders/<int:id>", methods=["DELETE"])
def delete_order(id):
    db = get_db()

    cursor = db.execute(
        "DELETE FROM orders WHERE id=?", (id,)
    )

    db.commit()
    db.close()

    if cursor.rowcount:
        return jsonify({"message": "Order deleted"})

    return jsonify({"error": "Order not found"}), 404


@app.route("/")
def home():
    return jsonify({
        "message": "Online Bakery Shop API",
        "status": "Running"
    })


if __name__ == "__main__":
    create_tables()
    app.run(host="0.0.0.0", port=5000, debug=True)