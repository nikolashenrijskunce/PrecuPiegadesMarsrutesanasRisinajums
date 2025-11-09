from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def connect():
    return redirect(url_for('auth.login'))

@main_bp.route('/home')
def home():
    return render_template('home.html')

@main_bp.route('/profile')
def profile():
    return render_template('profile.html')

@main_bp.route('/admin')
def admin():
    return redirect(url_for('main.driver', name='admin_1'))

@main_bp.route('/<name>')
def driver(name):
    return f'<h1>Driver: {name}</h1>'
