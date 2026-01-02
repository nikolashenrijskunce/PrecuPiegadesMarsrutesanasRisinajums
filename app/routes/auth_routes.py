from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
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
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        # login success -> go to profile

        # conn = sqlite3.connect('database.db')
        # cursor = conn.cursor()
        # user_info = cursor.execute("SELECT * FROM clients WHERE email = username").fetchone()
        # # if user_info:
        # #     user = user_info
        # # user_info = cursor.execute("SELECT * FROM drivers WHERE driver_id = user_id").fetchone()
        # # if user_info:
        # #     user = user_info
        # login_user(user_info, remember=False)

        del password

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT client_id, name, address, phone
            FROM clients
            WHERE name = ?
        """, (email,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return redirect(url_for("auth.login"))

        client_id, client_email, client_address, client_phone = row

        session.clear()
        session["role"] = "client"
        session["client_id"] = client_id
        session["client_email"] = client_email
        session["client_address"] = client_address
        session["client_phone"] = client_phone

        return redirect(url_for("client.home"))

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

        # Checks if user already exists
        #TODO: Correct email function
        user_info = cursor.execute("SELECT * FROM clients WHERE email = email").fetchone()
        if user_info:
            flash('Email address already exists')
            return redirect(url_for('auth.register'))

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

#TODO: sataisit logout
# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('auth.login'))

@auth_bp.route('/termsandconditions')
def termsandconditions():
    return render_template('authorization/terms_cond.html')