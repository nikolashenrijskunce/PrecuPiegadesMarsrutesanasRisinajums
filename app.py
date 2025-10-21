from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

# visas lapas ir definētas, kā funkcijas, kas ved uz kādu html failu no templates mapes, un vēl padod tam datus

@app.route('/')
def hello_world():  # put application's code here
    return render_template("home.html")

@app.route('/orders')
def order():  # put application's code here
    return render_template("orders.html", order_amount=7, order_list=["00001", "00002", "00003", "00004", "00005", "00006", "00007"])

@app.route('/orders/<orderid>')
def order_by_id(orderid):  # put application's code here
    return render_template("order_details.html", order_id=orderid)

@app.route('/<name>')
def driver(name):  # put application's code here
    return '<h1>Driver: ' + name + '</h1>'

@app.route('/admin')
def admin():  # put application's code here
    # return redirect(url_for('hello_world'))
    return redirect(url_for('driver', name='admin_1'))

if __name__ == '__main__':
    app.run()
