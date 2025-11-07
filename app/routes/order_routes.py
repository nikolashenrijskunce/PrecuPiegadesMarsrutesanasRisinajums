from flask import Blueprint, render_template

order_bp = Blueprint('order', __name__)

@order_bp.route('/')
def orders():
    return render_template('orders/orders.html',
                           order_amount=7,
                           order_list=['00001','00002','00003','00004','00005','00006','00007'])

@order_bp.route('/<orderid>')
def order_by_id(orderid):
    return render_template('orders/order_details.html', order_id=orderid)
