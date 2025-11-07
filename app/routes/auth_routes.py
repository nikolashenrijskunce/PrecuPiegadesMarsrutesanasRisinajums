from flask import Blueprint, render_template, request, redirect, url_for
# from app import bcrypt
from app.utils.security import verify_login

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['pwd']

        if not verify_login(username, password):
            return redirect(url_for('auth.login'))

        return render_template('profile.html', user=username)

    return render_template('authorization/login.html')
