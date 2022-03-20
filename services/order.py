from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Order(db.Model):
    __tablename__ = 'orders'

    orderID = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    customerName = db.Column(db.String(100), nullable=False)
    orderAddress = db.Column(db.String(100), nullable=False)
    orderDateTime = db.Column(db.datetime, nullable=False)
    orderDetail = db.Column(db.String(200), nullable=False)
    trackingNum = db.Column(db.Integer, nullable=False)
    orderStatus = db.Column(db.String(50), nullable=False)
    deliveryDate = db.Column(db.datetime, nullable=False)
    # filePath = db.Column(db.String(100), nullable=False)

    def __init__(self, orderID, customerName, orderAddress, orderDateTime, orderDetail, trackingNum, orderStatus, deliveryDate):
        self.orderID = orderID
        self.customerName = customerName
        self.orderAddress = orderAddress
        self.orderDateTime = orderDateTime
        self.orderDetail = orderDetail
        self.trackingNum = trackingNum
        self.orderStatus = orderStatus
        self.deliveryDate = deliveryDate
        # self.filePath = filePath

    def json(self):
        return {"orderID": self.orderID, "customerName": self.customerName, "orderAddress": self.orderAddress, "orderDateTime": self.orderDateTime, "orderDetail": self.orderDetail, "trackingNum": self.trackingNum, "orderStatus": self.orderStatus, "deliveryDate": self.deliveryDate}

# display all order info
@app.route("/orders")
def get_all():
    orderlist = Order.query.all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [orderlist.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404

# import data from excel, generate delivery date = today + 3 days, generate random tracking number
@app.route("/orders", methods=['POST'])
def create_orders():

    # data = pd.read_excel("")

    # cursor.execute("SELECT count(*) FROM ")
    # data = {
    #     'orderID':
    #     'customerName':
    #     'orderAddress':
    #     'orderDateTime':
    #     'orderDetail':
    #     'trackingNum':
    #     'orderStatus':
    #     'deliveryDate':
    # }
    # orders = Order(None, **data)

    try:
        db.session.add(orders)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the order."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": orders.json()
        }
    ), 201

# track order status
@app.route("/orders/<int:trackingNum>")
def get_by_trackingnum(trackingNum):
    order = Order.query.filter_by(trackingNum=trackingNum).first()
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Tracking Number not found."
        }
    ), 404

# update order status
@app.route("/orders/<int:trackingNum>", methods=['PUT'])
def update_by_trackingnum(trackingNum):
    try: 
        order = Order.query.filter_by(trackingNum=trackingNum).first()
        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": { order
                },
                    "message": "Order not found."
                }
            ), 404
            
        # update order status
        data = request.get_json()
        if data:
            order.orderStatus = data
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": order.json(),
                    "message": "Order Status Updated."
                }
            ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "trackingNum": trackingNum
                },
                "message": "An error occurred while updating the status. " + str(e)
            }
        ), 500

if __name__ == "__main__":
    app.run(port="5000", debug=True)