from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from os import environ
from sqlalchemy import ForeignKey


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/shinobilorry'
# environ.get('order_URL') or "http://localhost:5001/order"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# uploads_dir = os.path.join('assets/img/donations')

db = SQLAlchemy(app)
CORS(app)

class Fulfilment(db.Model):
    __tablename__ = 'fulfilment'
    
    fulfilment_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id = db.Column(db.Integer, nullable=False)
    driver_id = db.Column(db.Integer, nullable=False)

    def json(self):
        return {"fulfilment_id": self.fulfilment_id, "order_id": self.order_id, "driver_id": self.driver_id}

# get fulfilmentlist
@app.route("/fulfilment/<int:driver_id>")
def getFulfilmentList():
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
@app.route("/fulfilment/<int:fulfilment_id>")
def getFulfilment(fulfilment_id):
    fulfilment = Fulfilment.query.filter_by(fulfilment_id=fulfilment_id).first()
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
    app.run(host="0.0.0.0", port="5002", debug=True)