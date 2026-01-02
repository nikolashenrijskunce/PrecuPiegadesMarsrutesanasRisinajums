# pievieno trukstošās kolonnas datubāzei, lai korekti uzrādas svars un cena

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}

def add_column_if_missing(cur, table, col_def):
    col_name = col_def.split()[0]
    cols = get_columns(cur, table)
    if col_name in cols:
        print(f"[OK] {table}.{col_name} already exists")
        return
    print(f"[ADD] {table}.{col_name}")
    cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")

def main():
    print("Using DB:", os.path.abspath(DB_PATH))
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    add_column_if_missing(cur, "orders", "package_description TEXT")
    add_column_if_missing(cur, "orders", "package_weight REAL")
    add_column_if_missing(cur, "orders", "special_instructions TEXT")

    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()