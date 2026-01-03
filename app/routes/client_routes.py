from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import login_required, current_user
import sqlite3
import os
from datetime import datetime
from app.utils.user_model import User

client_bp = Blueprint('client', __name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database.db")
templates_path = 'pages_client'

# --- helpers for optional DB columns (to keep old DBs from crashing) ---
def _orders_columns(cursor):
    cursor.execute("PRAGMA table_info(orders)")
    return {row[1] for row in cursor.fetchall()}  # column names

def _has_cols(cursor, *cols):
    existing = _orders_columns(cursor)
    return all(c in existing for c in cols)


# \/ SO NEMAINIT, JO SIS AIZVED UZ LOGIN PAGE, KAD ATVER MAJASLAPU \/
@client_bp.route('/')
def connect():
    return redirect(url_for('auth.login'))
# /\ SO NEMAINIT, JO SIS AIZVED UZ LOGIN PAGE, KAD ATVER MAJASLAPU /\

@client_bp.route('/home')
@login_required
def home():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # client_id = session.get('client_id', 1)
    client_id = current_user.id

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
@login_required
def profile():
    client_id = current_user.id
    # if not client_id:
    #     return redirect(url_for("auth.login"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT client_id, name, address, phone
        FROM clients
        WHERE client_id = ?
    """, (client_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return redirect(url_for("auth.login"))

    client = {
        'client_id': row[0],
        'email': row[1],
        'address': row[2],
        'phone': row[3],
    }

    return render_template(f"{templates_path}/profile.html", client=client)

@client_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    client_id = current_user.id
    # if not client_id:
    #     return redirect(url_for('auth.login'))

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if request.method == 'POST':
        new_email = request.form['email'].strip()
        new_address = request.form['address'].strip()
        new_phone = request.form['phone'].strip()

        cur.execute("""
            UPDATE clients
            SET name = ?, address = ?, phone = ?
            WHERE client_id = ?
        """, (new_email, new_address, new_phone, client_id))

        conn.commit()
        conn.close()
        return redirect(url_for('client.profile'))

    # GET: load existing data
    cur.execute("SELECT name, address, phone FROM clients WHERE client_id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return "Client not found", 404

    client = {"email": row[0], "address": row[1], "phone": row[2]}
    return render_template(f"{templates_path}/profile_edit.html", client=client)


@client_bp.route('/orders')
@login_required
def orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # client_id = session.get('client_id', 1)  # TODO: use logged-in client_id
    client_id = current_user.id

    # If the DB has the newer columns, use them; otherwise fall back to the legacy schema.
    if _has_cols(cursor, 'package_description', 'package_weight', 'special_instructions'):
        cursor.execute("""
            SELECT
                o.order_id,
                o.status,
                o.pickup_address,
                o.delivery_address,
                o.estimated_delivery_time,
                COALESCE(o.package_description, GROUP_CONCAT(p.name, ', '), '') AS package_description,
                COALESCE(o.package_weight, SUM(p.weight * oi.quantity), 0)         AS package_weight,
                COALESCE(o.price, SUM(p.price * oi.quantity), 0)                  AS price,
                COALESCE(o.special_instructions, '')                              AS special_instructions
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id = o.order_id
            LEFT JOIN products p ON p.product_id = oi.product_id
            WHERE o.client_id = ?
            GROUP BY o.order_id
            ORDER BY o.order_date DESC
        """, (client_id,))
    else:
        cursor.execute("""
            SELECT
                o.order_id,
                o.status,
                o.pickup_address,
                o.delivery_address,
                o.estimated_delivery_time,
                ''  AS package_description,
                0.0 AS package_weight,
                COALESCE(o.price, 0) AS price,
                ''  AS special_instructions
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
            'estimated_delivery_time': row[4],
            'packageDescription': row[5],
            'packageWeight': row[6],
            'price': row[7],
            'specialInstructions': row[8],
        })

    return render_template(f'{templates_path}/orders/orders.html',
                           order_amount=len(order_list),
                           order_list=order_list)

@client_bp.route('/orders/<orderid>')
@login_required
def order_by_id(orderid):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if _has_cols(cursor, 'package_description', 'package_weight', 'special_instructions'):
        cursor.execute("""
            SELECT
                o.order_id,
                o.order_date,
                o.status,
                o.pickup_address,
                o.delivery_address,
                o.estimated_delivery_time,
                o.driver_name,
                o.vehicle_id,
                COALESCE(o.package_description, GROUP_CONCAT(p.name, ', '), '') AS package_description,
                COALESCE(o.package_weight, SUM(p.weight * oi.quantity), 0)         AS package_weight,
                COALESCE(o.price, SUM(p.price * oi.quantity), 0)                  AS price,
                COALESCE(o.special_instructions, '')                              AS special_instructions,
                c.name  AS client_name,
                c.phone AS client_phone,
                c.address AS client_address
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id = o.order_id
            LEFT JOIN products p ON p.product_id = oi.product_id
            LEFT JOIN clients c ON o.client_id = c.client_id
            WHERE o.order_id = ?
            GROUP BY o.order_id
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
            packageDescription=order_row[8],
            packageWeight=order_row[9],
            price=order_row[10],
            specialInstructions=order_row[11],
            clientName=order_row[12],
            clientPhone=order_row[13],
            clientAddress=order_row[14],
        )
        conn.close()
        return render_template(f'{templates_path}/orders/order_details.html', order=order)

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
               c.address,
               COALESCE(o.price, 0)
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
        clientAddress=order_row[10],
        price=order_row[11],
        packageDescription='',
        packageWeight=0.0,
        specialInstructions=''
    )

    cursor.execute("""
        SELECT p.name, p.weight, p.price, oi.quantity
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    """, (orderid,))
    items = cursor.fetchall()
    conn.close()

    if items:
        total_weight = sum(item[1] * item[3] for item in items)
        total_price = sum(item[2] * item[3] for item in items)
        package_description = ", ".join([item[0] for item in items])
        order['packageWeight'] = total_weight
        order['packageDescription'] = package_description
        order['price'] = total_price

    return render_template(f'{templates_path}/orders/order_details.html', order=order)

@client_bp.route('/orders/make', methods=['GET', 'POST'])
@login_required
def make_order():
    if request.method == 'POST':
        # client_id = session.get('client_id')  # jābūt ielogotam
        client_id = current_user.id

        pickup_address = request.form['pickup_address']
        delivery_address = request.form['delivery_address']
        package_description = request.form['package_description']
        package_weight = float(request.form['package_weight'])
        special_instructions = request.form.get('special_instructions', '')
        price = float(request.form['price'])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if _has_cols(cursor, 'package_description', 'package_weight', 'special_instructions'):
            cursor.execute("""
                INSERT INTO orders (
                    client_id, order_date, status,
                    pickup_address, delivery_address,
                    package_description, package_weight,
                    special_instructions, price
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_id,
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                'pending',
                pickup_address,
                delivery_address,
                package_description,
                package_weight,
                special_instructions,
                price
            ))
        else:
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
