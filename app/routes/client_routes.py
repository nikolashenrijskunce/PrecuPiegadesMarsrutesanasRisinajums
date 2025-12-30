from flask import Blueprint, render_template, redirect, url_for, request, session
import sqlite3
import os
from datetime import datetime

client_bp = Blueprint('client', __name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database.db")
templates_path = 'pages_client'

# \/ SO NEMAINIT, JO SIS AIZVED UZ LOGIN PAGE, KAD ATVER MAJASLAPU \/
@client_bp.route('/')
def connect():
    return redirect(url_for('auth.login'))
# /\ SO NEMAINIT, JO SIS AIZVED UZ LOGIN PAGE, KAD ATVER MAJASLAPU /\

@client_bp.route('/home')
def home():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    client_id = session.get('client_id', 1)  # pagaidām demo

    cursor.execute("""
        SELECT order_id,
               status,
               pickup_address,
               delivery_address,
               estimated_delivery_time,
               driver_name,
               price
        FROM orders
        WHERE client_id = ?
          AND status NOT IN ('delivered', 'cancelled')
        ORDER BY order_date DESC
        LIMIT 1
    """, (client_id,))

    row = cursor.fetchone()
    conn.close()

    current_order = None
    if row:
        current_order = {
            'id': row[0],
            'status': row[1],
            'pickup_address': row[2],
            'delivery_address': row[3],
            'estimated_delivery_time': row[4],
            'driver_name': row[5],
            'price': row[6]
        }

    return render_template(
        f'{templates_path}/home.html',
        current_order=current_order
    )


@client_bp.route('/profile')
def profile():
    return render_template(f'{templates_path}/profile.html')

@client_bp.route('/orders')
def orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    client_id = session.get('client_id', 1)  # Šeit vēlāk jāizmanto current_user.client_id
    cursor.execute("""
        SELECT o.order_id, o.status, o.pickup_address, o.delivery_address,
               o.estimated_delivery_time
        FROM orders o
        WHERE o.client_id = ?
        ORDER BY o.order_date DESC
    """, (client_id,))
    rows = cursor.fetchall()
    conn.close()

    order_list = []
    for row in rows:
        order_list.append({
            'order_id': row[0],
            'status': row[1],
            'pickup_address': row[2],
            'delivery_address': row[3],
            'packageDescription': "Demo product",  # vēlāk aprēķināt no order_items + products
            'price': 12.50  # vēlāk aprēķināt
        })

    return render_template('{templates_path}/orders/orders.html', order_amount=len(order_list), order_list=order_list)

@client_bp.route('/orders/<orderid>')
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

@client_bp.route('/orders/make', methods=['GET', 'POST'])
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

        return redirect(url_for('client.orders'))

    return render_template(f'pages_client/orders/make_order.html')


# \/ so var lietot kaa piemeru, ja vajag, lai atver lapu, kurai padod specifisku informaciju FUNKCIJAA \/

# @main_bp.route('/admin')
# def admin():
#     return redirect(url_for('main.driver', name='admin_1'))

# \/ so var lietot kaa piemeru, ja vajag, lai atver lapu, kurai padod specifisku informaciju URL ADRESE \/

# @main_bp.route('/<name>')
# def driver(name):
#     return f'<h1>Driver: {name}</h1>'
