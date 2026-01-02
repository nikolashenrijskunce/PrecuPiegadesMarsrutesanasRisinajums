from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt
from app.utils.security import verify_login

import os
#print("USING DB PATH:", os.path.abspath('database.db'))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # goes up from /routes to /app
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "database.db")

auth_bp = Blueprint('auth', __name__)

# ---------------------------
# LOGIN ROUTE
# ---------------------------
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        password = request.form.get("pwd", "")

        if not email or not password:
            del password
            return redirect(url_for("auth.login"))

        if not verify_login(email, password):
            # failed login -> stay on login page
            del password
            return redirect(url_for('auth.login'))
        # login success -> go to profile
        del password

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT client_id FROM clients WHERE name = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            session.clear()
            return redirect(url_for("auth.login"))

        client_id = row[0]

        # start clean session
        session.clear()
        session["client_id"] = client_id
        session["client_email"] = email
        session["role"] = "client"

        # go to client home (recommended instead of rendering profile.html directly)
        return redirect(url_for("client.home"))

        # GET -> show login page
    return render_template("authorization/login.html")


# ---------------------------
# REGISTER ROUTE
# ---------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # match your HTML input names
        email = request.form['email']
        password = request.form['pwd']
        address = request.form['address']
        city = request.form['city']
        zip_code = request.form['zip']

        # combine address info
        full_address = f"{address}, {city}, {zip_code}"

        # hash password securely
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # insert into clients table
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (name, address, phone, password)
            VALUES (?, ?, ?, ?)
        ''', (email, full_address, "", hashed_pw))
        print("Trying to insert:", email, full_address, "", hashed_pw)
        conn.commit()
        print("Committed successfully")
        conn.close()

        # redirect to login page after successful registration
        return redirect(url_for('auth.login'))

    # display the form
    return render_template('authorization/register.html')

@auth_bp.route('/termsandconditions')
def termsandconditions():
    return render_template('authorization/terms_cond.html')