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

# uploads_dir = os.path.join('assets/img/donations')

db = SQLAlchemy(app)
CORS(app)

class Fulfilment(db.Model):
    __tablename__ = 'fulfilment'
    
    fulfilmentID = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    orderID = db.Column(db.Integer, nullable=False)
    driverID = db.Column(db.Integer, nullable=False)

    def json(self):
        return {"fulfilmentID": self.fulfilmentID, "orderID": self.orderID, "driverID": self.driverID}

# get fulfilmentlist
@app.route("/fulfilmentlist")
def getAllFulfilment():
    fulfilmentlist = Fulfilment.query.all()
    if len(fulfilmentlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "items": [fulfilment.json() for fulfilment in fulfilmentlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no fulfilments."
        }
    ), 404

# get all fulfilments from database
@app.route("/fulfilment")
def getAllFulfilment():
    fulfilmentlist = Fulfilment.query.all()
    if len(fulfilmentlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "items": [fulfilment.json() for fulfilment in fulfilmentlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no fulfilments."
        }
    ), 404

# get specific fulfilment
@app.route("/fulfilment/<int:fulfilmentID>")
def getFulfilment(fulfilmentID):
    fulfilment = Fulfilment.query.filter_by(fulfilmentID=fulfilmentID).first()
    if fulfilment:
        return jsonify(
            {
                "code": 200,
                "data":  fulfilment.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No fulfilment was found."
        }
    ), 404

# create new field
@app.route('/fulfilment', methods=['POST'])
def createFulfilment():
    data = request.get_json()
    item = Fulfilment(**data)
    if ( request.get_json() is not None ): 
        try:
            db.session.add(item)
            db.session.commit()
            return jsonify(item.json()), 201
        except Exception:
            return jsonify({
                "message": "Unable to commit to database."
            }), 500

if __name__ == "__main__":
    app.run(port="5002", debug=True)
