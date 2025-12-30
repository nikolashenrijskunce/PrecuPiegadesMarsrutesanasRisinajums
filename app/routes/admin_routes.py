from flask import Blueprint, render_template, redirect, url_for, request, session
import sqlite3
import os
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database.db")
templates_path = 'pages_admin'

@admin_bp.route('/home')
def home():
    return render_template(f'{templates_path}/home.html')

@admin_bp.route('/profile')
def profile():
    return render_template(f'{templates_path}/profile.html')

@admin_bp.route('/orders')
def orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Izvēlamies visus pasūtījumus, neatkarīgi no klienta
    cursor.execute("""
        SELECT o.order_id,
               o.status,
               o.pickup_address,
               o.delivery_address,
               o.estimated_delivery_time,
               c.name
        FROM orders o
        LEFT JOIN clients c ON o.client_id = c.client_id
        ORDER BY o.order_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    order_list = []
    for row in rows:
        order_list.append({
            'order_id': row[0],
            'status': row[1],
            'pickup_address': row[2],
            'delivery_address': row[3],
            'estimated_delivery_time': datetime.strptime(row[4], '%Y-%m-%d %H:%M') if row[4] else None,
            'clientName': row[5] or 'Unknown',
            'packageDescription': "Demo product",  # vēlāk aprēķināt no order_items + products
            'price': 12.50,  # vēlāk aprēķināt
            'clientName': row[5] if len(row) > 5 else '-',
            'driverName': row[6] if len(row) > 6 else '-'
        })

    return render_template(
        f'{templates_path}/orders/orders.html',
        order_amount=len(order_list),
        order_list=order_list, now=datetime.now())

@admin_bp.route('/orders/<orderid>')
def order_by_id(orderid):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get order info
    cursor.execute("""
                   SELECT o.order_id,
                          o.order_date,
                          o.status,
                          o.pickup_address,
                          o.delivery_address,
                          o.estimated_delivery_time,
                          o.driver_name,
                          o.vehicle_id,
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
        status=order_row[2],
        pickupAddress=order_row[3],
        deliveryAddress=order_row[4],
        estimatedDeliveryTime=order_row[5],
        driverName=order_row[6],
        vehicleId=order_row[7],
        clientName=order_row[8],
        clientPhone=order_row[9],
        clientAddress=order_row[10]
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
    total_weight = sum(item[1] * item[3] for item in items)
    total_price = sum(item[2] * item[3] for item in items)
    package_description = ", ".join([item[0] for item in items])

    order['packageWeight'] = total_weight
    order['packageDescription'] = package_description
    order['price'] = total_price

    return render_template(f'{templates_path}/orders/order_details.html', order=order)


@admin_bp.route('/vehicles')
def vehicles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT vehicle_id, model, year, mileage, fuel_consumption, technical_inspection_expiry, status FROM vehicles")
    rows = cursor.fetchall()
    conn.close()

    vehicle_list = []
    for row in rows:
        vehicle_list.append({
            'vehicle_id': row[0],
            'model': row[1],
            'year': row[2],
            'mileage': row[3],
            'fuel_consumption': row[4],
            'technical_inspection_expiry': row[5],
            'status': row[6]
        })

    return render_template(f'{templates_path}/vehicles/vehicles.html',
                           vehicle_amount=len(vehicle_list),
                           vehicle_list=vehicle_list)


@admin_bp.route('/vehicles/<vehicleid>')
def vehicles_by_id(vehicleid):
    conn = sqlite3.connect(DB_PATH)
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
        'vehicle_id': row[0],
        'model': row[1],
        'year': row[2],
        'mileage': row[3],
        'fuel_consumption': row[4],
        'technical_inspection_expiry': row[5],
        'status': row[6]
    }

    return render_template(f'{templates_path}/vehicles/vehicle_details.html', vehicle=vehicle)


@admin_bp.route('/orders/make', methods=['GET', 'POST'])
def make_order():
    if request.method == 'POST':
        client_id = session.get('client_id')  # jābūt ielogotam

        pickup_address = request.form['pickup_address']
        delivery_address = request.form['delivery_address']
        package_description = request.form['package_description']
        package_weight = float(request.form['package_weight'])
        special_instructions = request.form.get('special_instructions', '')
        price = float(request.form['price'])

        conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch drivers
    cursor.execute("""
        SELECT d.driver_id, d.name, d.email, d.phone, d.vehicle_id, d.hours_worked, d.status,
               v.model, v.vehicle_id
        FROM drivers d
        LEFT JOIN vehicles v ON d.vehicle_id = v.vehicle_id
    """)
    rows = cursor.fetchall()
    conn.close()

    drivers_list = []
    for row in rows:
        drivers_list.append({
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'phone': row[3],
            'vehicle': {'model': row[7], 'license_plate': row[8]} if row[4] else None,
            'hours_worked': row[5] or 0,
            'status': row[6]
        })

    return render_template('pages_admin/drivers/drivers.html', drivers=drivers_list)

# \/ so var lietot kaa piemeru, ja vajag, lai atver lapu, kurai padod specifisku informaciju FUNKCIJAA \/

# @main_bp.route('/admin')
# def admin():
#     return redirect(url_for('main.driver', name='admin_1'))

# \/ so var lietot kaa piemeru, ja vajag, lai atver lapu, kurai padod specifisku informaciju URL ADRESE \/

# @main_bp.route('/<name>')
# def driver(name):
#     return f'<h1>Driver: {name}</h1>'