import sqlite3

import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def optimize_routes(orders):
    """
    MVP optimizācija:
    - vienmērīgi sadala orders pa driveriem
    - piešķir ETA secīgi
    - atgriež datus DB saglabāšanai
    """
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM drivers
        ORDER BY driver_id
    """)

    rows = cursor.fetchall()
    conn.close()

    drivers = [row[0] for row in rows]
    start_time = datetime.now()
    optimized = []

    for i, order in enumerate(orders):
        driver = drivers[i % len(drivers)]
        eta = start_time + timedelta(minutes=15 * i)

        optimized.append({
            "order_id": order["order_id"],
            "driver_name": driver,
            "eta": eta.strftime("%Y-%m-%d %H:%M:%S")
        })

    return optimized