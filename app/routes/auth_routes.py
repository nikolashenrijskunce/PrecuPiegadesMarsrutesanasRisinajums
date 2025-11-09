from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import bcrypt
from app.utils.security import verify_login

import os
#print("USING DB PATH:", os.path.abspath('database.db'))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # goes up from /routes to /app
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "sql_command_implementation", "database.db")

auth_bp = Blueprint('auth', __name__)

# ---------------------------
# LOGIN ROUTE
# ---------------------------
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['pwd']

        if not verify_login(username, password):
            # failed login -> stay on login page
            return redirect(url_for('auth.login'))

        # login success -> go to profile
        return render_template('profile.html', user=username)

    return render_template('authorization/login.html')


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
        conn.commit()
        conn.close()

        # redirect to login page after successful registration
        return redirect(url_for('auth.login'))

    # display the form
    return render_template('authorization/register.html')
