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


# Insert 5 sample orders
pickup_address = "Zunda krastmala 10, Kurzemes rajons, Rīga, LV-1048"

orders = [
    {
        "client_id": 1,
        "delivery_address": "Pils laukums 3, Centra rajons, Rīga, LV-1050",
        "driver_name": "Mark Davis",
        "vehicle_id": "TRK-03",
        "price": 120.50
    },
    {
        "client_id": 2,
        "delivery_address": "Vienības gat. 194A, Zemgales priekšpilsēta, Rīga, LV-1058",
        "driver_name": "Anna Johnson",
        "vehicle_id": "TRK-01",
        "price": 95.00
    },
    {
        "client_id": 3,
        "delivery_address": "Uriekstes iela 8A, Ziemeļu rajons, Rīga, LV-1005",
        "driver_name": "Peter Brown",
        "vehicle_id": "TRK-02",
        "price": 110.00
    },
    {
        "client_id": 4,
        "delivery_address": "Brīvības iela 76, Centra rajons, Rīga, LV-1001",
        "driver_name": "John Smith",
        "vehicle_id": "TRK-01",
        "price": 130.00
    },
    {
        "client_id": 5,
        "delivery_address": "Maskavas iela 250, Latgales priekšpilsēta, Rīga, LV-1063",
        "driver_name": "Mark Davis",
        "vehicle_id": "TRK-03",
        "price": 105.75
    }
]

order_date = "2026-01-01"

for order in orders:
    cursor.execute("""
        INSERT INTO orders (
            client_id,
            order_date,
            pickup_address,
            delivery_address,
            estimated_delivery_time,
            driver_name,
            vehicle_id,
            price
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order["client_id"],
        order_date,
        pickup_address,
        order["delivery_address"],
        None,                     # Estimated delivery time left as NULL for now
        order["driver_name"],
        order["vehicle_id"],
        order["price"]
    ))

conn.commit()

print("✅ Inserted 5 sample orders with real drivers")



vehicle_models = ["Mercedes Sprinter", "Volvo FH", "Scania R-Series"]

vehicles = []
for i, vid in enumerate(["TRK-01", "TRK-02", "TRK-03"]):
    model = random.choice(vehicle_models)
    year = random.randint(2015, 2023)
    mileage = random.randint(50000, 300000)
    fuel_consumption = round(random.uniform(8.0, 25.0), 1)
    inspection_date = f"2025-{random.randint(1,12):02}-15"
    vehicles.append((vid, model, year, mileage, fuel_consumption, inspection_date))

cursor.executemany("""
INSERT OR REPLACE INTO vehicles
(vehicle_id, model, year, mileage, fuel_consumption, technical_inspection_expiry)
VALUES (?, ?, ?, ?, ?, ?)
""", vehicles)

print("✅ Inserted sample vehicles")

# Sample driver names, statuses and vehicles
driver_names = ["John Smith", "Anna Johnson", "Peter Brown", "Laura White", "Mark Davis"]

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

    drivers.append((name, email, phone, vehicle_id, hours_worked))

# Insert into DB
cursor.executemany("""
INSERT INTO drivers
(name, email, phone, vehicle_id, hours_worked)
VALUES (?, ?, ?, ?, ?)
""", drivers)

conn.commit()
conn.close()

print("🎉 Data inserted successfully into database.db!")