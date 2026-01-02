import sqlite3
import random
import bcrypt

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

    # 🔒 generate a random password for each client (optional)
    plain_password = f"password{i:03}"
    hashed_pw = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())

    clients.append((company, address, phone, hashed_pw))

cursor.executemany(
    'INSERT INTO clients (name, address, phone, password) VALUES (?, ?, ?, ?)',
    clients
)
print("✅ Inserted 50 clients with hashed passwords")

# Insert 100 products
product_types = ["Laptop", "Monitor", "Chair", "Desk", "Keyboard", "Mouse", "Printer", "Tablet", "Headset",
                 "Docking Station"]
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

# Sample addresses
pickup_addresses = [
    "Rīgas iela 1, Rīga",
    "Brīvības iela 10, Rīga",
    "Lāčplēša iela 5, Rīga"
]

delivery_addresses = [
    "Daugavas iela 20, Rīga",
    "Valdemāra iela 8, Rīga",
    "Baznīcas iela 3, Rīga"
]

driver_names = ["Jānis B.", "Anna K.", "Pēteris S."]
vehicle_ids = ["TRK-01", "TRK-02", "TRK-03"]

#for order_id in range(1, 6):  # 5 sample orders
#    client_id = random.randint(1, 50)
#    order_date = "2025-11-05"
#    status = random.choice(["pending", "assigned", "in_transit", "delivered", "cancelled"])
#    pickup_address = random.choice(pickup_addresses)
#    delivery_address = random.choice(delivery_addresses)
#    estimated_delivery_time = "2025-11-06 14:00"
#    driver_name = random.choice(driver_names)
#    vehicle_id = random.choice(vehicle_ids)
#    price = round(random.uniform(25, 1500), 2)
#    cursor.execute("""
#                   INSERT INTO orders
#                   (client_id, order_date, status, pickup_address, delivery_address, estimated_delivery_time,
#                    driver_name, vehicle_id, price)
#                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#                   """, (client_id, order_date, status, pickup_address, delivery_address, estimated_delivery_time,
#                         driver_name, vehicle_id, price))

#    new_order_id = cursor.lastrowid

    # Add random order items
#    for _ in range(random.randint(1, 4)):
#        product_id = random.randint(1, 100)
#        quantity = random.randint(1, 5)
#        cursor.execute(
#            'INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)',
#            (new_order_id, product_id, quantity)
#        )

# Manually insert ONE order
client_id = 1
order_date = "2026-01-01"
status = "assigned"
pickup_address = "Ķīpsalas iela 6a, Kurzemes rajons, Rīga, LV-1048"
delivery_address = "Pils laukums 3, Centra rajons, Rīga, LV-1050"
estimated_delivery_time = "2026-01-02 15:00"
driver_name = "Jānis B."
vehicle_id = "TRK-01"
price = 120.50

cursor.execute("""
    INSERT INTO orders
    (client_id, order_date, status, pickup_address, delivery_address,
     estimated_delivery_time, driver_name, vehicle_id, price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    client_id,
    order_date,
    status,
    pickup_address,
    delivery_address,
    estimated_delivery_time,
    driver_name,
    vehicle_id,
    price
))

order_id = cursor.lastrowid


client_id = 1
order_date = "2026-01-01"
status = "assigned"
pickup_address = "Ķīpsalas iela 6a, Kurzemes rajons, Rīga, LV-1048"
delivery_address = "Pils laukums 3, Centra rajons, Rīga, LV-1050"
estimated_delivery_time = "2026-01-02 15:00"
driver_name = "Jānis B."
vehicle_id = "TRK-01"
price = 120.50

cursor.execute("""
    INSERT INTO orders
    (client_id, order_date, status, pickup_address, delivery_address,
     estimated_delivery_time, driver_name, vehicle_id, price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    client_id,
    order_date,
    status,
    pickup_address,
    delivery_address,
    estimated_delivery_time,
    driver_name,
    vehicle_id,
    price
))

order_id = cursor.lastrowid





print("✅ Inserted 5 sample orders with random items")
vehicle_models = ["Mercedes Sprinter", "Volvo FH", "Scania R-Series"]
vehicle_statuses = ["active", "maintenance", "inactive"]

vehicles = []
for i, vid in enumerate(["TRK-01", "TRK-02", "TRK-03"]):
    model = random.choice(vehicle_models)
    year = random.randint(2015, 2023)
    mileage = random.randint(50000, 300000)
    fuel_consumption = round(random.uniform(8.0, 25.0), 1)
    inspection_date = f"2025-{random.randint(1,12):02}-15"
    status = random.choice(vehicle_statuses)
    vehicles.append((vid, model, year, mileage, fuel_consumption, inspection_date, status))

cursor.executemany("""
INSERT OR REPLACE INTO vehicles
(vehicle_id, model, year, mileage, fuel_consumption, technical_inspection_expiry, status)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", vehicles)

print("✅ Inserted sample vehicles")

# Sample driver names, statuses and vehicles
driver_names = ["John Smith", "Anna Johnson", "Peter Brown", "Laura White", "Mark Davis"]
driver_statuses = ["available", "busy", "offline"]

# Fetch existing vehicle IDs from vehicles table
cursor.execute("SELECT vehicle_id FROM vehicles")
vehicle_rows = cursor.fetchall()
vehicle_ids = [v[0] for v in vehicle_rows]

# Generate demo driver data
drivers = []
for i in range(5):  # 5 sample drivers
    name = random.choice(driver_names)
    email = f"{name.lower().replace(' ', '.')}@example.com"
    phone = f"+371 2{random.randint(1000000, 9999999)}"
    vehicle_id = random.choice(vehicle_ids) if vehicle_ids else None
    hours_worked = round(random.uniform(0, 160), 1)  # monthly hours
    status = random.choice(driver_statuses)
    drivers.append((name, email, phone, vehicle_id, hours_worked, status))

# Insert into DB
cursor.executemany("""
INSERT INTO drivers
(name, email, phone, vehicle_id, hours_worked, status)
VALUES (?, ?, ?, ?, ?, ?)
""", drivers)

conn.commit()
conn.close()

print("🎉 Data inserted successfully into database.db!")