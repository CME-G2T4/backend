from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from flask_cors import CORS
from datetime import datetime
import os
from os import environ
from sqlalchemy import ForeignKey
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/shinobilorry'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)

class Inventory(db.Model):
    __tablename__ = 'inventory'

    inventoryID = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    orderID = db.Column(db.Integer, nullable=False)
    lotNum = db.Column(db.Integer, nullable=False)
   
    def __init__(self, inventoryID, orderID, lotNum):
        self.inventoryID = inventoryID
        self.orderID = orderID
        self.lotNum = lotNum

    def json(self):
        return {"inventoryID": self.inventoryID, "orderID": self.orderID, "lotNum": self.lotNum}

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
@app.route("/inventory/<int:lotNum>")
def get_by_orderID(orderID):
    lot = Inventory.query.filter_by(lotNum=lotNum).first()
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

if __name__ == "__main__":
    app.run(port="5001", debug=True)

