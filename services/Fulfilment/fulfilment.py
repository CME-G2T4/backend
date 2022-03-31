from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date
import os
from os import environ


app = Flask(__name__)

# dbURL = 'mysql+mysqlconnector://admin:password@database-1.cqnvz4nypbvo.us-east-1.rds.amazonaws.com/CME'
# dbURL = 'mysql+mysqlconnector://root@localhost:3306/shinobilorry'
dbURL = environ.get('dbURL') or 'mysql+mysqlconnector://root@host.docker.internal:3306/shinobilorry'
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}


db = SQLAlchemy(app)
CORS(app)

class Fulfilment(db.Model):
    __tablename__ = 'fulfilment'
    
    fulfilment_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    order_id = db.Column(db.Integer, nullable=False)
    driver_id = db.Column(db.Integer, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    order_address = db.Column(db.String(255), nullable=False)

    def json(self):
        return {"fulfilment_id": self.fulfilment_id, "order_id": self.order_id, "driver_id": self.driver_id, "delivery_date": self.delivery_date, "order_address": self.order_address}

# get fulfilmentlist
@app.route("/fulfilmentlist/<int:driver_id>")
def getFulfilmentList(driver_id):
    today = date.today()
    print(today)
    fulfilmentlist = Fulfilment.query.filter_by(driver_id=driver_id, delivery_date=today).all()
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
            "message": "There are no fulfilments for today."
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
                "data": {
                    "items": fulfilment.json()
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No fulfilment found."
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