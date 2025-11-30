from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main', __name__)

# \/ SO NEMAINIT, JO SIS AIZVED UZ LOGIN PAGE, KAD ATVER MAJASLAPU \/
@main_bp.route('/')
def connect():
    return redirect(url_for('auth.login'))
# /\ SO NEMAINIT, JO SIS AIZVED UZ LOGIN PAGE, KAD ATVER MAJASLAPU /\

@main_bp.route('/home')
def home():
    return render_template('pages_client/home.html')

@main_bp.route('/profile')
def profile():
    return render_template('pages_client/profile.html')


# \/ so var lietot kaa piemeru, ja vajag, lai atver lapu, kurai padod specifisku informaciju FUNKCIJAA \/

# @main_bp.route('/admin')
# def admin():
#     return redirect(url_for('main.driver', name='admin_1'))

# \/ so var lietot kaa piemeru, ja vajag, lai atver lapu, kurai padod specifisku informaciju URL ADRESE \/

# @main_bp.route('/<name>')
# def driver(name):
#     return f'<h1>Driver: {name}</h1>'
