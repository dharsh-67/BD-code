const express = require("express");
const sqlite3 = require("sqlite3").verbose();

const app = express();
app.use(express.json());

const db = new sqlite3.Database("bakery.db");

// Create tables
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, email TEXT UNIQUE, address TEXT
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, category TEXT, description TEXT,
        price REAL, availability INTEGER DEFAULT 1
    )`);

    db.run(`CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, product_id INTEGER, quantity INTEGER,
        flavor TEXT, size TEXT, delivery_type TEXT,
        delivery_address TEXT, status TEXT DEFAULT 'Pending'
    )`);
});

// ---------------- USERS ----------------

// Create user
app.post("/users", (req, res) => {
    const {name, phone, email, address} = req.body;

    db.run(
        `INSERT INTO users(name,phone,email,address) VALUES(?,?,?,?)`,
        [name, phone, email, address],
        function(err) {
            if (err) return res.status(400).json({error: err.message});
            res.json({message:"User created", user_id:this.lastID});
        }
    );
});

// Get users
app.get("/users", (req, res) => {
    db.all("SELECT * FROM users", [], (err, rows) => {
        res.json(rows);
    });
});

// Get one user
app.get("/users/:id", (req, res) => {
    db.get("SELECT * FROM users WHERE id=?", [req.params.id],
        (err, row) => res.json(row || {error:"User not found"}));
});

// Update user
app.put("/users/:id", (req, res) => {
    const {name, phone, email, address} = req.body;

    db.run(
        `UPDATE users SET name=?,phone=?,email=?,address=? WHERE id=?`,
        [name, phone, email, address, req.params.id],
        function(err) {
            res.json({message: this.changes ? "User updated" : "User not found"});
        }
    );
});

// Delete user
app.delete("/users/:id", (req, res) => {
    db.run("DELETE FROM users WHERE id=?", [req.params.id],
        function() {
            res.json({message: this.changes ? "User deleted" : "User not found"});
        });
});


// ---------------- PRODUCTS ----------------

// Create product
app.post("/products", (req, res) => {
    const {name, category, description, price, availability=1} = req.body;

    db.run(
        `INSERT INTO products
        (name,category,description,price,availability)
        VALUES(?,?,?,?,?)`,
        [name, category, description, price, availability],
        function(err) {
            if (err) return res.status(400).json({error:err.message});
            res.json({message:"Product created", product_id:this.lastID});
        }
    );
});

// Get products
app.get("/products", (req, res) => {
    db.all("SELECT * FROM products", [], (err, rows) => {
        res.json(rows);
    });
});

// Get one product
app.get("/products/:id", (req, res) => {
    db.get("SELECT * FROM products WHERE id=?", [req.params.id],
        (err, row) => res.json(row || {error:"Product not found"}));
});

// Update product
app.put("/products/:id", (req, res) => {
    const {name, category, description, price, availability} = req.body;

    db.run(
        `UPDATE products SET name=?,category=?,description=?,
        price=?,availability=? WHERE id=?`,
        [name, category, description, price, availability, req.params.id],
        function() {
            res.json({
                message:this.changes ? "Product updated" : "Product not found"
            });
        }
    );
});

// Delete product
app.delete("/products/:id", (req, res) => {
    db.run("DELETE FROM products WHERE id=?", [req.params.id],
        function() {
            res.json({
                message:this.changes ? "Product deleted" : "Product not found"
            });
        });
});


// ---------------- ORDERS ----------------

// Create order
app.post("/orders", (req, res) => {
    const {
        user_id, product_id, quantity,
        flavor, size, delivery_type, delivery_address
    } = req.body;

    db.run(
        `INSERT INTO orders
        (user_id,product_id,quantity,flavor,size,delivery_type,delivery_address)
        VALUES(?,?,?,?,?,?,?)`,
        [user_id, product_id, quantity, flavor, size,
         delivery_type, delivery_address],
        function(err) {
            if (err) return res.status(400).json({error:err.message});
            res.json({message:"Order placed", order_id:this.lastID});
        }
    );
});

// Get orders
app.get("/orders", (req, res) => {
    db.all(`
        SELECT orders.id, users.name AS customer,
        products.name AS product, orders.quantity,
        orders.flavor, orders.size,
        orders.delivery_type, orders.delivery_address,
        orders.status
        FROM orders
        JOIN users ON orders.user_id=users.id
        JOIN products ON orders.product_id=products.id
    `, [], (err, rows) => {
        res.json(rows);
    });
});

// Get one order
app.get("/orders/:id", (req, res) => {
    db.get(`
        SELECT orders.*, users.name AS customer,
        products.name AS product
        FROM orders
        JOIN users ON orders.user_id=users.id
        JOIN products ON orders.product_id=products.id
        WHERE orders.id=?
    `, [req.params.id], (err, row) => {
        res.json(row || {error:"Order not found"});
    });
});

// Update order
app.put("/orders/:id", (req, res) => {
    const {status, delivery_address} = req.body;

    db.run(
        `UPDATE orders SET status=?,delivery_address=? WHERE id=?`,
        [status, delivery_address, req.params.id],
        function() {
            res.json({
                message:this.changes ? "Order updated" : "Order not found"
            });
        }
    );
});

// Delete order
app.delete("/orders/:id", (req, res) => {
    db.run("DELETE FROM orders WHERE id=?", [req.params.id],
        function() {
            res.json({
                message:this.changes ? "Order deleted" : "Order not found"
            });
        }
    );
});


// Home
app.get("/", (req, res) => {
    res.json({
        message:"Online Bakery Shop API",
        status:"Running"
    });
});


// Start server
app.listen(5000, () => {
    console.log("Server running at http://localhost:5000");
});