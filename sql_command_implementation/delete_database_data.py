import sqlite3
import os

# Absolūtais ceļš uz datubāzi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Saraksts ar tabulām, kuras vēlamies attīrīt
tables = ["clients", "products", "orders", "order_items"]

for table in tables:
    cursor.execute(f"DELETE FROM {table}")
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")  # Reset AUTOINCREMENT
    print(f"✅ Tabula '{table}' ir iztīrīta un AUTOINCREMENT resetēts.")

conn.commit()
conn.close()

print("🎉 Visas tabulas iztīrītas!")