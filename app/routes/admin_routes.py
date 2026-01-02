from flask import Blueprint, render_template, redirect, url_for, request, session
import sqlite3
import os
from datetime import datetime

# IMPORTANT: šis imports ir pareizais tavai struktūrai (app/utils/route_calc.py)
from app.utils.route_calc import optimize_routes

admin_bp = Blueprint('admin', __name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database.db")
templates_path = 'pages_admin'


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@admin_bp.route('/home')
def home():
    return render_template(f'{templates_path}/home.html')


@admin_bp.route('/profile')
def profile():
    return render_template(f'{templates_path}/profile.html')


@admin_bp.route('/orders')
def orders():
    conn = get_conn()
    cursor = conn.cursor()

    # 1) Paņem pending orderus optimizācijai
    cursor.execute("""
        SELECT o.order_id, o.pickup_address, o.delivery_address
        FROM orders o
        WHERE o.status = 'pending'
    """)
    raw_orders = cursor.fetchall()

    # 2) Ja ir ko optimizēt -> izrēķina un saglabā DB
    if raw_orders:
        orders_for_opt = [{
            "order_id": r["order_id"],
            "pickup": r["pickup_address"],
            "delivery": r["delivery_address"]
        } for r in raw_orders]

        optimized_orders = optimize_routes(orders_for_opt)

        for o in optimized_orders:
            # o jābūt: {"order_id": ..., "driver_name": ..., "eta": "..."}
            cursor.execute("""
                UPDATE orders
                SET driver_name = ?,
                    estimated_delivery_time = ?
                WHERE order_id = ?
            """, (o["driver_name"], o["eta"], o["order_id"]))

        conn.commit()

    # 3) Tagad ielasa visus orderus UI (ar driver + ETA)
    cursor.execute("""
        SELECT o.order_id,
               o.status,
               o.pickup_address,
               o.delivery_address,
               o.estimated_delivery_time,
               c.name AS client_name,
               o.driver_name,
               o.price
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.client_id
        ORDER BY o.order_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    order_list = []
    for row in rows:
        order_list.append({
            'order_id': row["order_id"],
            'status': row["status"],
            'pickup_address': row["pickup_address"],
            'delivery_address': row["delivery_address"],
            'estimated_delivery_time': row["estimated_delivery_time"],
            'clientName': row["client_name"] or '-',
            'driverName': row["driver_name"] or '-',
            'price': float(row["price"]) if row["price"] is not None else 12.50
        })

    return render_template(
        f'{templates_path}/orders/orders.html',
        order_amount=len(order_list),
        order_list=order_list,
        now=datetime.now()
    )


@admin_bp.route('/orders/<orderid>')
def order_by_id(orderid):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.order_id,
               o.order_date,
               o.status,
               o.pickup_address,
               o.delivery_address,
               o.estimated_delivery_time,
               o.driver_name,
               o.vehicle_id,
               c.name AS client_name,
               c.phone AS client_phone,
               c.address AS client_address
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.client_id
        WHERE o.order_id = ?
    """, (orderid,))
    order_row = cursor.fetchone()

    if not order_row:
        conn.close()
        return "Order not found", 404

    order = dict(
        order_id=order_row["order_id"],
        order_date=order_row["order_date"],
        status=order_row["status"],
        pickupAddress=order_row["pickup_address"],
        deliveryAddress=order_row["delivery_address"],
        estimatedDeliveryTime=order_row["estimated_delivery_time"],
        driverName=order_row["driver_name"],
        vehicleId=order_row["vehicle_id"],
        clientName=order_row["client_name"],
        clientPhone=order_row["client_phone"],
        clientAddress=order_row["client_address"]
    )

    cursor.execute("""
        SELECT p.name, p.weight, p.price, oi.quantity
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    """, (orderid,))
    items = cursor.fetchall()
    conn.close()

    total_weight = sum((item["weight"] or 0) * (item["quantity"] or 0) for item in items)
    total_price = sum((item["price"] or 0) * (item["quantity"] or 0) for item in items)
    package_description = ", ".join([item["name"] for item in items]) if items else ""

    order['packageWeight'] = total_weight
    order['packageDescription'] = package_description
    order['price'] = total_price

    return render_template(f'{templates_path}/orders/order_details.html', order=order)


@admin_bp.route('/vehicles')
def vehicles():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vehicle_id, model, year, mileage, fuel_consumption, technical_inspection_expiry, status
        FROM vehicles
    """)
    rows = cursor.fetchall()
    conn.close()

    vehicle_list = []
    for row in rows:
        vehicle_list.append({
            'vehicle_id': row["vehicle_id"],
            'model': row["model"],
            'year': row["year"],
            'mileage': row["mileage"],
            'fuel_consumption': row["fuel_consumption"],
            'technical_inspection_expiry': row["technical_inspection_expiry"],
            'status': row["status"]
        })

    return render_template(
        f'{templates_path}/vehicles/vehicles.html',
        vehicle_amount=len(vehicle_list),
        vehicle_list=vehicle_list
    )


@admin_bp.route('/vehicles/<vehicleid>')
def vehicles_by_id(vehicleid):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vehicle_id, model, year, mileage, fuel_consumption, technical_inspection_expiry, status
        FROM vehicles
        WHERE vehicle_id = ?
    """, (vehicleid,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Vehicle not found", 404

    vehicle = {
        'vehicle_id': row["vehicle_id"],
        'model': row["model"],
        'year': row["year"],
        'mileage': row["mileage"],
        'fuel_consumption': row["fuel_consumption"],
        'technical_inspection_expiry': row["technical_inspection_expiry"],
        'status': row["status"]
    }

    return render_template(f'{templates_path}/vehicles/vehicle_details.html', vehicle=vehicle)


@admin_bp.route('/orders/make', methods=['GET', 'POST'])
def make_order():
    if request.method == 'POST':
        client_id = session.get('client_id')  # jābūt ielogotam

        pickup_address = request.form['pickup_address']
        delivery_address = request.form['delivery_address']
        package_description = request.form['package_description']  # (pašlaik DB neliekam, ok)
        package_weight = float(request.form['package_weight'])    # (pašlaik DB neliekam, ok)
        special_instructions = request.form.get('special_instructions', '')
        price = float(request.form['price'])

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO orders (client_id, order_date, status, pickup_address, delivery_address, price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            'pending',
            pickup_address,
            delivery_address,
            price
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('admin.orders'))

    return render_template(f'{templates_path}/orders/make_order.html')


@admin_bp.route('/drivers')
def drivers():
    conn = get_conn()
    cursor = conn.cursor()

    # NOTE: vehicles tabulā nav license_plate, tāpēc rādam tikai model + vehicle_id
    cursor.execute("""
        SELECT d.driver_id, d.name, d.email, d.phone,
               d.vehicle_id,
               v.model
        FROM drivers d
        LEFT JOIN vehicles v ON d.vehicle_id = v.vehicle_id
        ORDER BY d.driver_id
    """)
    rows = cursor.fetchall()
    conn.close()

    drivers_list = []
    for row in rows:
        drivers_list.append({
            'id': row["driver_id"],
            'name': row["name"],
            'email': row["email"],
            'phone': row["phone"],
            'vehicle': {
                'model': row["model"],
                'vehicle_id': row["vehicle_id"]
            } if row["vehicle_id"] else None
        })

    return render_template('pages_admin/drivers/drivers.html', drivers=drivers_list)


@admin_bp.route('/drivers/<int:driver_id>/plan')
def driver_plan(driver_id):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT driver_id, name, email, phone
        FROM drivers
        WHERE driver_id = ?
    """, (driver_id,))
    d = cursor.fetchone()

    if not d:
        conn.close()
        return "Driver not found", 404

    driver = {
        "id": d["driver_id"],
        "name": d["name"],
        "email": d["email"],
        "phone": d["phone"]
    }

    # Ielasa orderus, kas DB piesaistīti šim driverim (driver_name jābūt tieši tādam pašam kā drivers.name)
    cursor.execute("""
        SELECT order_id, delivery_address, estimated_delivery_time
        FROM orders
        WHERE driver_name = ?
        ORDER BY estimated_delivery_time
    """, (driver["name"],))
    rows = cursor.fetchall()
    conn.close()

    orders = []
    for r in rows:
        orders.append({
            "order_id": r["order_id"],
            "address": r["delivery_address"],
            "eta": r["estimated_delivery_time"]
        })

    return render_template(
        "pages_admin/drivers/driver_plan.html",
        driver=driver,
        orders=orders
    )
