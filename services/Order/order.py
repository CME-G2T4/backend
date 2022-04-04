from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from os import environ
import sqlalchemy
import pandas as pd
import random
import requests
import pymysql
import boto3
from openpyxl import Workbook
from tempfile import NamedTemporaryFile
import uuid
from botocore.exceptions import ClientError

app = Flask(__name__)

dbURL = environ.get('dbURL') or 'mysql+pymysql://admin:password@pt-test.cziuplds1j4w.ap-southeast-1.rds.amazonaws.com/CME'
inventoryURL = environ.get('inventoryURL') or 'http://127.0.0.1:5001'
awsAccessKeyId= environ.get('awsAccessKeyId')
awsSecretAccessKey = environ.get('awsSecretAccessKey')
awsRegion = environ.get('region') or 'ap-southeast-1'
s3OrderBucket = environ.get('s3OrderBucket') or 'shinobilorry-order-file'

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

    order_id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(354), nullable=False)
    order_address = db.Column(db.String(255), nullable=False)
    order_datetime = db.Column(db.DateTime, nullable=False)
    order_details = db.Column(db.String(255), nullable=False)
    tracking_no = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.String(50), nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, order_id, customer_name, customer_email, order_address, order_datetime, order_details, tracking_no, order_status, delivery_date):
        self.order_id = order_id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.order_address = order_address
        self.order_datetime = order_datetime
        self.orderDetail = order_details
        self.tracking_no = tracking_no
        self.order_status = order_status
        self.delivery_date = delivery_date

    def toJson(self):
        return {"order_id": self.order_id, "customer_name": self.customer_name, "customer_email": self.customer_email, "order_address": self.order_address, "order_datetime": self.order_datetime, "order_details": self.order_details, "tracking_no": self.tracking_no, "order_status": self.order_status, "delivery_date": self.delivery_date}

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

def send_email(customer_name, customer_email, tracking_no):
    client = boto3.client('ses',
                        aws_access_key_id=awsAccessKeyId,
                        aws_secret_access_key=awsSecretAccessKey,
                        region_name=awsRegion) # Connect to ses

    SENDER = "delivery@shinobilorry.ninja"

    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = customer_email # To replace with customer_email

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = awsRegion

    # The subject line for the email.
    SUBJECT = "Shinobilorry - Your Tracking Information"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = (f"Dear {customer_name},\r\n\n"
                f"We've got your parcel! Sit tight and it will be with you in a jiffy!\r\n"
                f"This is your tracking ID {tracking_no}.\r\n\n"
                f"Thank you."
                )         

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    # client = boto3.client('ses',region_name='us-east-1')

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,

        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

# import data from excel, generate delivery date = today + 3 days, generate random tracking number
@app.route("/orders", methods=['POST'])
def create_orders():

    filename = request.files['filename'] #retrieve excel name from frontend field
    s3_resource = boto3.resource('s3',
                                aws_access_key_id=awsAccessKeyId,
                                aws_secret_access_key=awsSecretAccessKey) # Connect to s3 resource

    dest_filename = "file_{}.xlsx".format(str(uuid.uuid4())[:8]) # File name to save inside aws

    # s3_resource.Bucket('itsmyawsbucket').upload_file(Filename=filename.temporary_file_path, Key=dest_filename,ExtraArgs={'ACL': 'public-read'})
    s3_resource.Bucket(s3OrderBucket).upload_fileobj(Fileobj=filename, Key=dest_filename,ExtraArgs={'ACL': 'public-read', 'ContentDisposition': "inline; filename="+filename, 'ContentType': "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }) # Fileobj - the file, need extra arguements to put content type or the file will be corrupted
    uploaded_data = s3_resource.Object(s3OrderBucket, dest_filename).get()

    data = pd.read_excel(uploaded_data['Body'].read())
    # data = pd.read_excel(request.files['filename'] )
    # print(data)
    
    # with NamedTemporaryFile() as tmp:
        # filename = '{}'.format(dest_filename)
        

    query = "INSERT INTO orders(customer_name,customer_email,order_address,order_datetime,order_details,tracking_no,order_status,delivery_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    # grab existing row count in the database for validation later
    cursor.execute("SELECT count(*) FROM orders")
    before_import = cursor.fetchone()
    print(data.shape[0])
    new_order_id = []
    for i,r in data.iterrows():
        customer_name = r['customer_name']
        customer_email = r['customer_email']
        order_address = r['order_address']
        order_datetime = r['order_datetime']
        order_details = r['order_details']
        tracking_no = random.randint(100000, 500000)
        while Order.query.filter_by(tracking_no=tracking_no).first():
            tracking_no = random.randint(100000, 500000)
        order_status = 'Pending'
        delivery_date = order_datetime + timedelta(days=3)
        
        values = (customer_name, customer_email, order_address, order_datetime.strftime('%Y-%m-%d %H:%M:%S'), order_details, tracking_no, order_status, delivery_date.strftime('%Y-%m-%d %H:%M:%S'))

        # Execute SQL query
        cursor.execute(query, values)
        new_order_id.append(cursor.lastrowid)
        send_email(customer_name, customer_email, tracking_no)

    connection.commit()

    for nid in new_order_id:
    #     # replace post url to inventory microservice on production
        inventory_response = requests.post(inventoryURL + f"/inventory", { "order_id": nid })

    # print(cursor.rowcount, "record(s) inserted")
    # check if all rows are imported
    # cursor.execute("SELECT count(*) FROM orders")
    # result = cursor.fetchone()

    return jsonify(
        {
            "code":200,
            "message": "Orders imported successfully."
            "inventory_response": inventory_response.text
        }
    ), 200

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