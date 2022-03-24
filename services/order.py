from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from os import environ
import sqlalchemy
import pandas as pd
import random
import requests

app = Flask(__name__)

dbURL = 'mysql+mysqldb://admin:password@database-1.cqnvz4nypbvo.us-east-1.rds.amazonaws.com/CME'
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)
engine = sqlalchemy.create_engine(dbURL)
connection = engine.raw_connection()
cursor = connection.cursor()

class Order(db.Model):
    __tablename__ = 'orders'

    orderID = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    customer_name = db.Column(db.String(100), nullable=False)
    order_address = db.Column(db.String(100), nullable=False)
    order_datetime = db.Column(db.DateTime, nullable=False)
    order_details = db.Column(db.String(200), nullable=False)
    tracking_no = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.String(50), nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    # filePath = db.Column(db.String(100), nullable=False)

    def __init__(self, orderID, customer_name, order_address, order_datetime, order_details, tracking_no, order_status, delivery_date):
        self.orderID = orderID
        self.customer_name = customer_name
        self.order_address = order_address
        self.order_datetime = order_datetime
        self.orderDetail = order_details
        self.tracking_no = tracking_no
        self.order_status = order_status
        self.delivery_date = delivery_date
        # self.filePath = filePath

    def toJson(self):
        return {"orderID": self.orderID, "customer_name": self.customer_name, "order_address": self.order_address, "order_datetime": self.order_datetime, "order_details": self.order_details, "tracking_no": self.tracking_no, "order_status": self.order_status, "delivery_date": self.delivery_date}

# display all order info
@app.route("/orders")
def get_all():
    orderlist = Order.query.all()
    # print(orderlist)
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [o.toJson() for o in orderlist]
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

    filename = request.files['filename'] #retrieve excel name from frontend field
    data = pd.read_excel(filename)

    query = "INSERT INTO orders(customer_name,order_address,order_datetime,order_details,tracking_no,order_status,delivery_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    # grab existing row count in the database for validation later
    cursor.execute("SELECT count(*) FROM orders")
    before_import = cursor.fetchone()
    print(data.shape[0])
    new_order_id = []
    for i,r in data.iterrows():
        customer_name = r['customer_name']
        order_address = r['order_address']
        order_datetime = r['order_datetime']
        order_details = r['order_details']
        tracking_no = random.randint(100000, 500000)
        while Order.query.filter_by(tracking_no=tracking_no).first():
            tracking_no = random.randint(100000, 500000)
        order_status = 'Pending'
        delivery_date = order_datetime + timedelta(days=3)
        
        values = (customer_name, order_address, order_datetime.strftime('%Y-%m-%d %H:%M:%S'), order_details, tracking_no, order_status, delivery_date.strftime('%Y-%m-%d %H:%M:%S'))

        # Execute SQL query
        cursor.execute(query, values)
        new_order_id.append(cursor.lastrowid)

    connection.commit()

    for nid in new_order_id:
        # replace post url to inventory microservice on production
        response = requests.post(f"http://127.0.0.1:5001/inventory", { "orderID": nid })

    print(cursor.rowcount, "record(s) inserted")
    # check if all rows are imported
    cursor.execute("SELECT count(*) FROM orders")
    result = cursor.fetchone()

    print((result[0] - before_import[0]) == len(data.index))  # should be True

# track order status
@app.route("/orders/<int:tracking_no>")
def get_by_trackingno(tracking_no):
    order = Order.query.filter_by(tracking_no=tracking_no).first()
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.toJson()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Tracking Number not found."
        }
    ), 404

# update order status
@app.route("/orders/<int:tracking_no>", methods=['PUT'])
def update_by_trackingno(tracking_no):
    try: 
        order = Order.query.filter_by(tracking_no=tracking_no).first()
        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": { 
                },
                    "message": "Order not found."
                }
            ), 404
            
        # update order status
        data = request.form['new_status'] # Change the value to whatever key is being passed through 
        if data:
            order.order_status = data
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": order.toJson(),
                    "message": "Order Status Updated."
                }
            ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "tracking_no": tracking_no
                },
                "message": "An error occurred while updating the status. " + str(e)
            }
        ), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)