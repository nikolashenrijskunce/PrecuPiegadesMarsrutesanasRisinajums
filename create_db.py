import sqlite3

import os
print("USING DB PATH:", os.path.abspath('database.db'))


conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.executescript('''
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS clients;

CREATE TABLE clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    weight REAL NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    pickup_address TEXT,
    delivery_address TEXT,
    estimated_delivery_time TEXT,
    driver_name TEXT,
    vehicle_id TEXT,
    price REAL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
''')

conn.commit()
conn.close()