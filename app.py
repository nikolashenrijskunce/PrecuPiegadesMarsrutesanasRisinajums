from flask import Flask, redirect, url_for, render_template, request
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
# visas lapas ir definētas, kā funkcijas, kas ved uz kādu html failu no templates mapes, un vēl padod tam datus

@app.route('/home')
def home():  # put application's code here
    return render_template('home.html')

@app.route('/orders')
def order():  # put application's code here
    return render_template('orders/orders.html', order_amount=7, order_list=['00001', '00002', '00003', '00004', '00005', '00006', '00007'])

@app.route('/orders/<orderid>')
def order_by_id(orderid):  # put application's code here
    return render_template('orders/order_details.html', order_id=orderid)

@app.route('/<name>')
def driver(name):  # put application's code here komentars komentars
    return '<h1>Driver: ' + name + '</h1>'

@app.route('/admin')
def admin():  # put application's code here
    # return redirect(url_for('hello_world'))
    return redirect(url_for('driver', name='admin_1'))

@app.route('/', methods=['GET', 'POST']) #login url, kas var ari darit post ne tikai get (parejiem defaultaa tikai get)
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['pwd']
        f = open('passwords.txt')
        stored_hash = f.readline()
        f.close()
        if username != 'admin' or bcrypt.check_password_hash(stored_hash, password) != True: #PAROLE IR "qwerty"
            del password, stored_hash
            return redirect(url_for('login'))
        del password, stored_hash
        return render_template('profile.html', user=username)
    else:
        return render_template('authoirzation/login.html')

@app.route('/profile')
def profile():  # put application's code here
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
