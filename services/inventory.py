from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from os import environ
import sqlalchemy
import random
import pymysql


app = Flask(__name__)

# dbURL = 'mysql+pymysql://admin:password@database-1.cqnvz4nypbvo.us-east-1.rds.amazonaws.com/CME'
# dbURL = 'mysql+pymysql://root@localhost:3306/shinobilorry'
dbURL = 'mysql+pymysql://root@host.docker.internal:3306/shinobilorry'
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)
engine = sqlalchemy.create_engine(dbURL) 
connection = engine.raw_connection()
cursor = connection.cursor()

class Inventory(db.Model):
    __tablename__ = 'inventory'

    inventory_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id = db.Column(db.Integer, nullable=False)
    lot_num = db.Column(db.Integer, nullable=False)
   
    def __init__(self, inventory_id, order_id, lot_num):
        self.inventory_id = inventory_id
        self.order_id = order_id
        self.lot_num = lot_num

    def json(self):
        return {"inventory_id": self.inventory_id, "order_id": self.order_id, "lot_num": self.lot_num}

@app.route("/inventory")
def get_all():
    inventorylist = Inventory.query.all()
    if len(inventorylist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [inventorylist.json() for lot in inventorylist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no lots."
        }
    ), 404

# retrieve parcel-to-lot information
@app.route("/inventory/<int:lot_num>")
def get_by_order_id(lot_num):
    lot = Inventory.query.filter_by(lot_num=lot_num).first()
    if lot:
        return jsonify(
            {
                "code": 200,
                "data": lot.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Lot not found."
        }
    ), 404

# assigning parcel to lot (automated - insert into inventory table after importing excel)
@app.route("/inventory", methods=["POST"])
def add_new_inventory():
    try:
        query = "INSERT INTO inventory(order_id,lot_num) VALUES (%s, %s)"
        lot_num = random.randint(1, 200)
        order_id = request.form["order_id"]
        values = (int(order_id), lot_num)
        cursor.execute(query, values)
        
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "order_id": order_id
                },
                "message": "An error occurred while updating the status. " + str(e)
            }
        ), 500
    connection.commit()
    print(cursor.rowcount, "record(s) inserted")
    return jsonify(
        {
            "code": 200,
            "message": "New order assigned successfully to a lot number."
        }
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5001", debug=True)

