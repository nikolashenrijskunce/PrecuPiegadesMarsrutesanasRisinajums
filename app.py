from flask import Flask, redirect, url_for

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/orders')
def order():  # put application's code here
    return '<h1>Current orders</h1>'

@app.route('/orders/<orderid>')
def order_by_id(orderid):  # put application's code here
    return f'<h1>Order (id:{orderid}) current status</h1>'

@app.route('/<name>')
def driver(name):  # put application's code here
    return '<h1>Driver: ' + name + '</h1>'

@app.route('/admin')
def admin():  # put application's code here
    # return redirect(url_for('hello_world'))
    return redirect(url_for('driver', name='admin_1'))

if __name__ == '__main__':
    app.run()
