from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
import sqlite3
import bcrypt
from app.utils.security import verify_login
from app.utils.user_model import User

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

        # parbauda, vai parole un epasts ir ierakstits
        if not email or not password:
            del password
            flash('Please enter your email/username and password!')
            return redirect(url_for("auth.login"))

        # parbauda, vai epasts un parole sakrit
        if not verify_login(email, password):
            # failed login -> stay on login page
            del password
            flash('Please check your login details and try again!')
            return redirect(url_for('auth.login'))
        # login success -> go to profile

        del password

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        user_info = cursor.execute(f"SELECT client_id, name FROM clients WHERE name = ?", (email,)).fetchone()
        if user_info:
            if user_info[1] == 'admin@example.com':
                user = User(user_info[0], 'admin')
            else:
                user = User(user_info[0], 'client')
        else:
            user_info = cursor.execute(f"SELECT driver_id FROM drivers WHERE email = ?", (email,)).fetchone()
            if not user_info:
                flash('Please check your login details and try again!')
                return redirect(url_for("auth.login"))
            user = User(user_info[0], 'driver')

        conn.close()

        login_user(user, remember=False)
        if user.get_roles() == 'client':
            return redirect(url_for("client.home"))
        elif user.get_roles() == 'driver':
            return redirect(url_for("driver.home"))
        elif user.get_roles() == 'admin':
            return redirect(url_for("admin.orders"))
        else:
            flash('Error has occured!')
            return redirect(url_for("auth.login"))

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
        phone = request.form['phone']

        # combine address info
        full_address = f"{address}, {city}, {zip_code}"

        # hash password securely
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # insert into clients table
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Checks if user already exists
        user_info = cursor.execute(f"SELECT * FROM clients WHERE name = ?", (email,)).fetchone()
        if user_info:
            flash('Email address already exists')
            return redirect(url_for('auth.register'))

        user_info = cursor.execute(f"SELECT * FROM drivers WHERE email = ?", (email,)).fetchone()
        if user_info:
            flash('You do not have permission to create a profile using work email!')
            return redirect(url_for('auth.register'))

        cursor.execute('''
            INSERT INTO clients (name, address, phone, password)
            VALUES (?, ?, ?, ?)
        ''', (email, full_address, phone, hashed_pw))
        print("Trying to insert:", email, full_address, phone, hashed_pw)
        conn.commit()
        print("Committed successfully")
        conn.close()

        # redirect to login page after successful registration
        return redirect(url_for('auth.login'))

    # display the form
    return render_template('authorization/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/termsandconditions')
def termsandconditions():
    return render_template('authorization/terms_cond.html')