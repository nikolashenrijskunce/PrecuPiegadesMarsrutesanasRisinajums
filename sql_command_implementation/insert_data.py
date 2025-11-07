import sqlite3
import random

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Insert 50 clients
cities = ["Rīga", "Jelgava", "Liepāja", "Ventspils", "Daugavpils"]
streets = ["Brīvības iela", "Lielā iela", "Ganību iela", "Pasta iela", "Skolas iela", "Park iela"]

clients = []
for i in range(1, 51):
    company = f"SIA Company_{i:03}"
    address = f"{random.choice(streets)} {random.randint(1, 50)}, {random.choice(cities)}"
    phone = f"+371 2{random.randint(1000000, 9999999)}"
    clients.append((company, address, phone))

cursor.executemany('INSERT INTO clients (name, address, phone) VALUES (?, ?, ?)', clients)
print("✅ Inserted 50 clients")

# Insert 100 products
product_types = ["Laptop", "Monitor", "Chair", "Desk", "Keyboard", "Mouse", "Printer", "Tablet", "Headset", "Docking Station"]
brands = ["HP", "Dell", "Lenovo", "ASUS", "Acer", "Logitech", "Canon", "Epson"]

products = []
for i in range(1, 101):
    name = f"{random.choice(brands)} {random.choice(product_types)} Model-{i:03}"
    weight = round(random.uniform(0.2, 25.0), 1)
    price = round(random.uniform(25, 1500), 2)
    products.append((name, weight, price))

cursor.executemany('INSERT INTO products (name, weight, price) VALUES (?, ?, ?)', products)
print("✅ Inserted 100 products")

# Insert sample orders
for order_id in range(1, 6):  # 5 sample orders
    client_id = random.randint(1, 50)
    order_date = "2025-11-05"
    status = "Pending"
    cursor.execute('INSERT INTO orders (client_id, order_date, status) VALUES (?, ?, ?)',
                   (client_id, order_date, status))
    new_order_id = cursor.lastrowid

    # Add random order items
    for _ in range(random.randint(1, 4)):
        product_id = random.randint(1, 100)
        quantity = random.randint(1, 5)
        cursor.execute('INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)',
                       (new_order_id, product_id, quantity))

print("✅ Inserted 5 sample orders with random items")

conn.commit()
conn.close()

print("🎉 Data inserted successfully into database.db!")