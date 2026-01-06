from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_required, current_user
import sqlite3
import os
from datetime import datetime
from app.utils.user_model import User, role_required

driver_bp = Blueprint('driver', __name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database.db")
templates_path = 'pages_driver'

@driver_bp.route('/home')
@login_required
@role_required('driver')
def home():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    driver_id = current_user.id

    # --- Driver ---
    cursor.execute("""
        SELECT name, hours_worked, vehicle_id
        FROM drivers
        WHERE driver_id = ?
    """, (driver_id,))
    driver_row = cursor.fetchone()

    if not driver_row:
        conn.close()
        return "Driver not found", 404

    driver = {
        "name": driver_row[0],
        "hours_worked": driver_row[1]
    }

    driver_name = driver_row[0]
    vehicle_id = driver_row[2]

    # --- Vehicle ---
    vehicle = None
    if vehicle_id:
        cursor.execute("""
            SELECT model, vehicle_id, mileage, technical_inspection_expiry
            FROM vehicles
            WHERE vehicle_id = ?
        """, (vehicle_id,))
        v = cursor.fetchone()

        if v:
            vehicle = {
                "model": v[0],
                "vehicle_id": v[1],
                "mileage": v[2],
                "inspection_expiry": v[3]
            }


    schedule = {
        "Monday": "08:00 - 17:00",
        "Tuesday": "08:00 - 17:00",
        "Wednesday": "08:00 - 17:00",
        "Thursday": "08:00 - 17:00",
        "Friday": "08:00 - 17:00"
    }

    return render_template(
        f'{templates_path}/home.html',
        driver=driver,
        vehicle=vehicle,
        schedule=schedule
    )

@driver_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('driver')
def profile():

    driver_id = current_user.id

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        # Update editable fields
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]

        cursor.execute("""
            UPDATE drivers
            SET name = ?, email = ?, phone = ?
            WHERE driver_id = ?
        """, (name, email, phone, driver_id))
        conn.commit()
        conn.close()

        return redirect(url_for('driver.profile'))

    # GET: load driver data
    cursor.execute("""
        SELECT name, email, phone, vehicle_id, hours_worked
        FROM drivers
        WHERE driver_id = ?
    """, (driver_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Driver not found", 404

    user = {
        "name": row[0],
        "email": row[1],
        "phone": row[2],
        "vehicle_id": row[3],
        "hours_worked": row[4]
    }

    is_editing = request.args.get("edit") == "1"

    return render_template("pages_driver/profile.html", user=user, is_editing=is_editing)

@driver_bp.route('/orders')
@login_required
@role_required('driver')
def orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    driver_id = current_user.id

    # Get driver info
    cursor.execute("""
        SELECT name, vehicle_id
        FROM drivers
        WHERE driver_id = ?
    """, (driver_id,))
    driver_row = cursor.fetchone()

    if not driver_row:
        conn.close()
        return "Driver not found", 404

    driver_name, vehicle_id = driver_row

    # Get orders
    cursor.execute("""
        SELECT
            order_id,
            pickup_address,
            delivery_address,
            estimated_delivery_time,
            price
        FROM orders
        WHERE driver_name = ?
        ORDER BY order_date DESC
    """, (driver_name,))

    rows = cursor.fetchall()
    conn.close()

    order_list = []
    for row in rows:
        order_list.append({
            "order_id": row[0],
            "pickup_address": row[1],
            "delivery_address": row[2],
            "estimated_delivery_time": row[3],
            "packageDescription": "Demo produkts",
            "price": row[4]
        })

    return render_template(
        f'{templates_path}/orders/orders.html',
        order_amount=len(order_list),
        order_list=order_list
    )

@driver_bp.route('/orders/<orderid>')
@login_required
@role_required('driver')
def order_by_id(orderid):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get order info
    cursor.execute("""
                   SELECT o.order_id,
                          o.order_date,
                          o.pickup_address,
                          o.delivery_address,
                          o.estimated_delivery_time,
                          o.driver_name,
                          c.name,
                          c.phone,
                          c.address
                   FROM orders o
                            LEFT JOIN clients c ON o.client_id = c.client_id
                   WHERE o.order_id = ?
                   """, (orderid,))
    order_row = cursor.fetchone()

    if not order_row:
        conn.close()
        return "Order not found", 404

    order = dict(
        order_id=order_row[0],
        order_date=order_row[1],
        pickupAddress=order_row[2],
        deliveryAddress=order_row[3],
        estimatedDeliveryTime=order_row[4],
        driverName=order_row[5],
        clientName=order_row[6],
        clientPhone=order_row[7],
        clientAddress=order_row[8]
    )

    # Get products for this order
    cursor.execute("""
                   SELECT p.name, p.weight, p.price, oi.quantity
                   FROM order_items oi
                            JOIN products p ON oi.product_id = p.product_id
                   WHERE oi.order_id = ?
                   """, (orderid,))
    items = cursor.fetchall()
    conn.close()

    # Calculate total weight and total price
    total_weight = sum(float(item[1]) * int(item[3]) for item in items)
    total_price = sum(float(item[2]) * int(item[3]) for item in items)
    package_description = ", ".join([item[0] for item in items])

    order['packageWeight'] = total_weight
    order['packageDescription'] = package_description
    order['price'] = total_price

    return render_template(f'{templates_path}/orders/order_details.html', order=order)
