from flask import Flask, request, Response, jsonify, render_template
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from sqlalchemy import desc, text
from sqlalchemy.dialects import mysql
from flasgger import Swagger, swag_from
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pika
import re
from flask_login import LoginManager, UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime, timedelta
import json
from flask_mail import Mail, Message
from secret_keys import *

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"]) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///craze.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER'] = {
    'title': 'BetterU API',
    'description': 'The available endpoints for the BetterU service.',
    'termsOfService': None,
    'doc_dir': './docs/',
    'uiversion': 3,
}

app.config['MAIL_SERVER']="smtp.gmail.com"
app.config['MAIL_PORT']="465"
app.config['MAIL_USERNAME']="betteru490@gmail.com"
app.config['MAIL_PASSWORD']=GMAIL_APP_PASSWORD
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True

app.config['SECRET_KEY'] = CRAZE_SECRET_KEY #super duper secret 🤫
app.config['SESSION_COOKIE_SECURE']=False

db = SQLAlchemy(app)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#API docs stuff
api = Api(app)
swag = Swagger(app)
mail = Mail(app)

mail.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))

class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    role = db.Column(db.Text, nullable=False)
    eula = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Text, nullable=False)
    def get_id(self):
        return str(self.user_id)

def order_prescription(medication_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='orders')
    channel.basic_publish(exchange='', routing_key='orders', body=str(medication_id))
    print(f"Ordered medication ID: {medication_id}")
    connection.close()
      
@app.route("/")
def home():
    return "<h1>It works!</h1>"

@app.route("/mail/<int:user_id>", methods=['POST'])
@swag_from("docs/email/post.yml")
def email(user_id):
    email_address = db.session.execute(text("SELECT email FROM users WHERE user_id = :uid"), {'uid': user_id}).first()
    if(email_address == None):
        return ResponseMessage("Could not send email. Invalid user.", 400)
    if(request.json.get('email_body') == None or request.json.get('email_body') == ""):
        return ResponseMessage("No email body.", 400)
    if(request.json.get('email_subject') == None or request.json.get('email_subject') == ""):
        return ResponseMessage("No email subject.", 400)
    msg = Message(
        subject=request.json.get('email_subject'),
        body=request.json.get('email_body'),
        sender="betteru490@gmail.com",
        recipients=[email_address.email],
    )
    result = mail.send(msg)
    print(msg, result)
    return ResponseMessage(f"Email sent to {email_address.email}", 200)

@app.route("/docs")
def docs():
    return render_template("build/html/index.html")

@app.route('/login', methods=['GET', 'POST'])
@swag_from("docs/auth/login_get.yml", methods=['GET'])
@swag_from("docs/auth/login_post.yml", methods=['POST'])
def login():
    next = request.args.get('next')
    valid_email = r"^.+\d*@.+[.][a-zA-Z]{2,4}$"
    params = {
        'email': None,
        'password': None,
        'remember': False
    }
    if(request.method == 'GET'):
        params['email'] = request.args.get('email')
        params['password'] = request.args.get('password')
        params['remember'] = request.args.get('remember') if request.args.get('remember') != None else False
    elif(request.method == 'POST'):
        json = request.json
        params['email'] = json.get('email')
        params['password'] = json.get('password')
        params['remember'] = json.get('remember') if json.get('remember') != None else False
    if(None in ( params['email'], params['password'])):
        return ResponseMessage("Required credentials not sent.", 400)
    if(re.search(valid_email, params['email']) == None):
        return ResponseMessage("Invalid email address.", 400)
    user = Users.query.filter_by(email=params['email']).first()
    if user == None:
        return ResponseMessage("Invalid user credentials.", 401)
    elif(user.password != params['password']):
        return ResponseMessage("Invalid password.", 400)
    else:
        login_user(user, params['remember'] or False)
        return {'user_id': current_user.user_id, 'role': current_user.role, 'message':'Login successful.'}

@app.route('/logout', methods=['GET', 'POST'])
@login_required
@swag_from('docs/auth/logout.yml', methods=['GET', 'POST'])
def logout():
    logout_user()
    return ResponseMessage("User Logged out.", 200)

@app.route('/login_check')
@login_required
@swag_from('docs/auth/login_check.yml')
def login_check():
    return ResponseMessage(f"User is logged in. ID: {current_user.get_id()}", 200)

@app.route("/transactions", methods=['GET'])
@login_required
@swag_from('docs/transactions/get.yml')
def get_transactions():
    print(current_user)
    #sql query
    query = "SELECT * FROM transactions\n"
    #get inputs
    params = {
        'cid': "" if request.args.get('creditcard_id') == None else request.args.get('creditcard_id'),
        'pid': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'did': "" if request.args.get('doctor_id') == None else request.args.get('doctor_id'),
        'tid': "" if request.args.get('transaction_id') == None else request.args.get('transaction_id'),
        'datetime': "" if request.args.get('created_at') == None else '%' + request.args.get('created_at') + '%'
    }
    if(params['pid'] != "" or params['did'] != "" or params['cid'] != "" or params['tid'] != "" or params['datetime'] != ""):
        query += ("WHERE " + ("creditcard_id = :cid\n" if params['cid'] != "" else "TRUE\n"))
        query += ("AND " + ("patient_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("doctor_id = :did\n" if params['did'] != "" else "TRUE\n"))
        query += ("AND " + ("transaction_id = :tid\n" if params['tid'] != "" else "TRUE\n"))
        query += ("AND " + ("created_at LIKE :datetime\n" if params['datetime'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'transactions': []}
    for row in result:
        json['transactions'].append({
            'creditcard_id': row.creditcard_id,
            'doctor_id': row.doctor_id,
            'patient_id': row.patient_id,
            'transaction_id': row.transaction_id,
            'created_at': row.created_at,
            'service_fee': row.service_fee,
            'doctor_fee': row.doctor_fee,
            'subtotal': row.subtotal
        })
    return json, 200

@app.route("/transactions/<int:transaction_id>", methods=['DELETE'])
@login_required
@swag_from('docs/transactions/delete.yml')
def delete_transaction(transaction_id):
    try:
        result = db.session.execute(text("SELECT * FROM transactions WHERE transaction_id = :transaction_id\n"), {'transaction_id': transaction_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM transactions WHERE transaction_id = :transaction_id\n"), {'transaction_id': transaction_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/saved_posts", methods=['GET'])
@login_required
@swag_from('docs/savedposts/get.yml')
def get_saved_posts():
    #sql query
    query = "SELECT * FROM saved_posts AS S JOIN users AS U ON S.user_id = U.user_id JOIN forum_posts AS F ON F.post_id = S.post_id\n"
    #get inputs
    params = {
        'uid': "" if request.args.get('user_id') == None else request.args.get('user_id'),
        'pid': "" if request.args.get('post_id') == None else request.args.get('post_id'),
        'datetime': "" if request.args.get('saved_at') == None else '%' + request.args.get('saved_at') + '%'
    }
    if(params['uid'] != "" or params['pid'] != "" or params['datetime'] != ""):
        query += ("WHERE " + ("S.user_id = :uid\n" if params['uid'] != "" else "TRUE\n"))
        query += ("AND " + ("S.post_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("S.saved_at LIKE :datetime\n" if params['datetime'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'saved_posts': []}
    for row in result:
        json['saved_posts'].append({
            'user_id': row.user_id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'post_id': row.post_id,
            'title': row.title,
            'saved_at': row.saved_at
        })
    return json, 200

@app.route("/saved_posts", methods=['DELETE'])
@login_required
@swag_from('docs/savedposts/delete.yml')
def delete_saved_posts():
    params = {
        'post_id': request.json.get('post_id'),
        'user_id': request.json.get('user_id')
    }
    try:
        result = db.session.execute(text("SELECT * FROM saved_posts WHERE post_id = :post_id AND user_id = :user_id\n"), {'post_id': params['post_id'], 'user_id': params['user_id']})
        if result.first() != None:
            db.session.execute(text("DELETE FROM saved_posts WHERE post_id = :post_id AND user_id = :user_id\n"), {'post_id': params['post_id'], 'user_id': params['user_id']})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/saved_posts", methods=['POST'])
@login_required
@swag_from('docs/savedposts/post.yml')
def add_saved_posts():
    query = text("""
        INSERT INTO saved_posts (user_id, post_id, saved_at)
        VALUES (
            :user_id,
            :post_id,
            CURRENT_TIMESTAMP)
    """)
    params = {
        'post_id': request.json.get('post_id'),
        'user_id': request.json.get('user_id')
    }
    #input validation
    if None in params.values():
        return ResponseMessage("Required parameters not supplied.", 400)
        #execute query
    try:
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Error Executing Query:\n{e}", 500)
    else:
        db.session.commit()
        return ResponseMessage(f"Post saved successfully", 201)

@app.route("/prescriptions", methods=['GET'])
@swag_from('docs/prescriptions/get.yml')
def get_prescriptions():
    #sql query
    query = "SELECT * FROM prescriptions\n"
    #get inputs
    params = {
        'prescriptid': "" if request.args.get('prescription_id') == None else request.args.get('prescription_id'),
        'pid': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'did': "" if request.args.get('doctor_id') == None else request.args.get('doctor_id'),
        'mid': "" if request.args.get('medication_id') == None else request.args.get('medication_id'),
        'phid': "" if request.args.get('pharmacist_id') == None else request.args.get('pharmacist_id'),
        'status': "" if request.args.get('status') == None else '%' + request.args.get('status') + '%',
        'datetime': "" if request.args.get('date_prescribed') == None else '%' + request.args.get('date_prescribed') + '%'
    }
    if(params['prescriptid'] != "" or params['pid'] != "" or params['did'] != "" or params['mid'] != "" or params['phid'] != "" or params['status'] != "" or params['datetime'] != ""):
        query += ("WHERE " + ("prescription_id = :prescriptid\n" if params['prescriptid'] != "" else "TRUE\n"))
        query += ("AND " + ("patient_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("doctor_id = :did\n" if params['did'] != "" else "TRUE\n"))
        query += ("AND " + ("medication_id = :mid\n" if params['mid'] != "" else "TRUE\n"))
        query += ("AND " + ("pharmacist_id = :phid\n" if params['phid'] != "" else "TRUE\n"))
        query += ("AND " + ("status LIKE :status\n" if params['status'] != "" else "TRUE\n"))
        query += ("AND " + ("date_prescribed LIKE :datetime\n" if params['datetime'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'prescriptions': []}
    for row in result:
        json['prescriptions'].append({
            'prescription_id': row.prescription_id,
            'doctor_id': row.doctor_id,
            'patient_id': row.patient_id,
            'medication_id': row.medication_id,
            'pharmacist_id': row.pharmacist_id,
            'status': row.status,
            'date_prescribed': row.date_prescribed,
            'instructions': row.instructions,
            'quantity': row.quantity
        })
    return json, 200

@app.route("/prescriptions/<int:prescription_id>", methods=['DELETE'])
@swag_from('docs/prescriptions/delete.yml')
def delete_prescriptions(prescription_id):
    try:
        result = db.session.execute(text("SELECT * FROM prescriptions WHERE prescription_id = :prescription_id\n"), {'prescription_id': prescription_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM prescriptions WHERE prescription_id = :prescription_id\n"), {'prescription_id': prescription_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/prescriptions/<int:prescription_id>", methods=['PATCH'])
@swag_from('docs/prescriptions/patch.yml')
def update_prescriptions(prescription_id):
    #sql query
    query = text(f"""
        UPDATE prescriptions SET
            doctor_id = {':doctor_id' if request.json.get('doctor_id') != None else 'doctor_id'},
            patient_id = {':patient_id' if request.json.get('patient_id') != None else 'patient_id'},
            medication_id = {':medication_id' if request.json.get('medication_id') != None else 'medication_id'},
            instructions = {':instructions' if request.json.get('instructions') != None else 'instructions'},
            status = {':status' if request.json.get('status') != None else 'status'},
            date_prescribed = {':date_prescribed' if request.json.get('date_prescribed') != None else 'date_prescribed'},
            quantity = {':quantity' if request.json.get('quantity') != None else 'quantity'},
            pharmacist_id = {':pharmacist_id' if request.json.get('pharmacist_id') != None else 'pharmacist_id'}
        WHERE prescription_id = :prescription_id
    """)
    params = {
        'prescription_id': prescription_id,
        'doctor_id': request.json.get('doctor_id'),
        'patient_id': request.json.get('patient_id'),
        'medication_id': request.json.get('medication_id'),
        'instructions': request.json.get('instructions'),
        'status': request.json.get('status'),
        'date_prescribed': request.json.get('date_prescribed'),
        'quantity': request.json.get('quantity'),
        'pharmacist_id': request.json.get('pharmacist_id')
    }
    #input validation
    if(db.session.execute(text("SELECT * FROM prescriptions WHERE prescription_id = :prescription_id"), params).first() == None):
        return ResponseMessage("Prescription not found.", 404)
    if all(param == None for param in list(params.values())[1:]):
        return ResponseMessage("No parameters were passed to update...", 200)
    if request.json.get('quantity') <= 0:
        return ResponseMessage("Quantity must be >0", 400)
    if(params['status'] != None and params['status'].lower() not in ('canceled', 'pending', 'rejected', 'accepted')):
        return ResponseMessage("Invalid status field. Must be ('canceled', 'pending', 'rejected', 'accepted')", 400)
    valid_datetime = r"^\d{4}-\d{2}-\d{2} [0-5][0-9]:[0-5][0-9]:[0-5][0-9]$"
    if(params['date_prescribed'] != None and re.search(valid_datetime, params['date_prescribed']) == None):
        return ResponseMessage("Invalid Start Time. Format: (yyyy-mm-dd hh:mm:ss)", 400)
    if(params['doctor_id'] != None and db.session.execute(text("SELECT * FROM doctors WHERE doctor_id = :doctor_id"), params).first() == None):
        return ResponseMessage("Invalid doctor ID.", 400)
    if(params['patient_id'] != None and db.session.execute(text("SELECT * FROM patients WHERE patient_id = :patient_id"), params).first() == None):
        return ResponseMessage("Invalid patient ID.", 400)
    if(params['medication_id'] != None and db.session.execute(text("SELECT * FROM medications WHERE medication_id = :medication_id"), params).first() == None):
        return ResponseMessage("Invalid medication ID.", 400)
    if(params['pharmacist_id'] != None and db.session.execute(text("SELECT * FROM pharmacists WHERE pharmacist_id = :pharmacist_id"), params).first() == None):
        return ResponseMessage("Invalid pharmacist ID.", 400)
    try:
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Server/SQL Error. Exeption: \n{e}", 500)
    else:
        db.session.commit()
        return ResponseMessage("Prescription Successfully Updated.", 200) 

@app.route("/prescriptions", methods=['POST'])
@swag_from('docs/prescriptions/post.yml')
def put_prescriptions():
    query = text("""
        INSERT INTO prescriptions (prescription_id, doctor_id, patient_id, medication_id, instructions, date_prescribed, status, quantity, pharmacist_id)
        VALUES (
            :prescription_id,
            :doctor_id,
            :patient_id,
            :medication_id,
            :instructions,
            CURRENT_TIMESTAMP,
            'pending',
            :quantity,
            :pharmacist_id)
    """)
    # NOTE: doing prescription_id this way could bring about a race condition.... but lets be real this is never happening.
    params = {
        'prescription_id': (db.session.execute(text("SELECT MAX(prescription_id) + 1 AS prescription_id FROM prescriptions")).first()).prescription_id,
        'doctor_id': request.json.get('doctor_id'),
        'patient_id': request.json.get('patient_id'),
        'medication_id': request.json.get('medication_id'),
        'instructions': request.json.get('instructions'),
        #'date_prescribed': request.json.get('date_prescribed'),
        #'status': request.json.get('status'),
        'quantity': request.json.get('quantity'),
        'pharmacist_id': request.json.get('pharmacist_id')
    }
    #input validation
    if None in params.values():
        return ResponseMessage("Required parameters not supplied.", 400)
    #valid_datetime = r"^\d{4}-\d{2}-\d{2} [0-5][0-9]:[0-5][0-9]:[0-5][0-9]$"
    #if((re.search(valid_datetime, request.json.get('date_prescribed'))) is None):
    #    return ResponseMessage("Invalid Datetime. Format: (yyyy-mm-dd hh:mm:ss)", 400)
    #if (request.json.get('status')).lower() not in ["accepted", "rejected", "pending", "canceled"]:
    #    return ResponseMessage("Invalid Status. Format: (`accepted`, `rejected`, `pending`, `canceled`)", 400)
    if request.json.get('quantity') <= 0:
        return ResponseMessage("Quantity must be > 0", 400)
    try:
        result = db.session.execute(text("SELECT * FROM patients WHERE patient_id = :patient_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid patient id.", 400)
        result = db.session.execute(text("SELECT * FROM doctors WHERE doctor_id = :doctor_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid doctor id.", 400)
        result = db.session.execute(text("SELECT * FROM pharmacists WHERE pharmacist_id = :pharmacist_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid pharmacist id.", 400)
        result = db.session.execute(text("SELECT * FROM medications WHERE medication_id = :medication_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid medication id.", 400)
        #execute query
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Error Executing Query:\n{e}", 500)
    else:
        db.session.commit()
        order_prescription(f"{params['medication_id']},{params['patient_id']}")
        return ResponseMessage(f"Prescription entry successfully created (id: {params['prescription_id']})", 201)

@app.route("/appointments", methods=['GET'])
@login_required
@swag_from('docs/appointments/get.yml')
def appointments():
    #sql query
    query = "SELECT * FROM appointments\n"
    #get inputs
    params = {
        'aid': "" if request.args.get('appointment_id') == None else request.args.get('appointment_id'),
        'did': "" if request.args.get('doctor_id') == None else request.args.get('doctor_id'),
        'pid': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'status': "" if request.args.get('status') == None else request.args.get('status'),
        'reason': "" if request.args.get('reason') == None else '%' + request.args.get('reason') + '%',
        'start_time': "" if request.args.get('start_time') == None else '%' + request.args.get('start_time') + '%',
        'order_by': "DESC" if request.args.get('order_by') == None else request.args.get('order_by')
    }
    if(params['aid'] != "" or params['did'] != "" or params['pid'] != "" or params['status'] != "" or params['reason'] != "" or params['start_time'] != "" or params['order_by'] != ""):
        query += ("WHERE " + ("appointment_id = :aid\n" if params['aid'] != "" else "TRUE\n"))
        query += ("AND " + ("doctor_id = :did\n" if params['did'] != "" else "TRUE\n"))
        query += ("AND " + ("patient_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("status = :status\n" if params['status'] != "" else "TRUE\n"))
        query += ("AND " + ("reason LIKE :reason\n" if params['reason'] != "" else "TRUE\n"))
        query += ("AND " + ("start_time LIKE :start_time\n" if params['start_time'] != "" else "TRUE\n"))
        query += (f"ORDER BY start_time {"ASC" if params['order_by'].upper() == "ASC" else "DESC"}") #the unsafe way but has limited values so its fine
    #execute query
    result = db.session.execute(text(query), params)
    json = {'appointments': []}
    for row in result:
        json['appointments'].append({
            'appointment_id': row.appointment_id,
            'doctor_id': row.doctor_id,
            'patient_id': row.patient_id,
            'start_time': row.start_time,
            'end_time': row.end_time,
            'status': row.status,
            'location': row.location,
            'reason': row.reason,
            'created_at': row.created_at,
            'details': row.details,
            'notes' : row.notes
        })
    return json, 200

@app.route("/appointments/<int:appointment_id>", methods=['DELETE'])
@login_required
@swag_from('docs/appointments/delete.yml')
def delete_appointments(appointment_id):
    try:
        result = db.session.execute(text("SELECT * FROM appointments WHERE appointment_id = :appointment_id\n"), {'appointment_id': appointment_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM appointments WHERE appointment_id = :appointment_id\n"), {'appointment_id': appointment_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/appointments", methods=['POST'])
@login_required
@swag_from('docs/appointments/post.yml')
def add_appointment():
    #sql query
    query = text("""
        INSERT INTO appointments (appointment_id, doctor_id, patient_id, start_time, end_time, status, location, reason, details, created_at, notes)
        VALUES (
            :appointment_id,
            :doctor_id,
            :patient_id,
            DATETIME(:start_time),
            DATETIME(:end_time),
            :status,
            :location,
            :reason,
            :details,
            CURRENT_TIMESTAMP,
            :notes)
    """)
    # NOTE: doing appointment_id this way could bring about a race condition.... but lets be real this is never happening.
    location = request.json.get('location')
    if location is None:
        location = ""
    details = request.json.get('details')
    if details is None:
        details = ""
    notes = request.json.get('notes')
    if notes is None:
        notes = ""

    valid_datetime = r"^\d{4}-\d{2}-\d{2} [0-5][0-9]:[0-5][0-9]:[0-5][0-9]$"
    if(request.json.get('start_time') != None and re.search(valid_datetime, request.json.get('start_time')) == None):
        return ResponseMessage("Invalid Start Time. Format: (yyyy-mm-dd hh:mm:ss)", 400)
    end_time = datetime.strptime(request.json.get('start_time'), "%Y-%m-%d %H:%M:%S")
    end_time = end_time + timedelta(hours=1)
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    params = {
        'appointment_id': (db.session.execute(text("SELECT MAX(appointment_id) + 1 AS appointment_id FROM appointments")).first()).appointment_id,
        'doctor_id': request.json.get('doctor_id'),
        'patient_id': request.json.get('patient_id'),
        'start_time': request.json.get('start_time'),
        'end_time': end_time,
        'status': request.json.get('status'),
        'location': location,
        'reason': request.json.get('reason'),
        'details': details,
        'notes': notes
    }
    #input validation
    if None in [request.json.get('doctor_id'), request.json.get('patient_id'), request.json.get('start_time'), request.json.get('status'), request.json.get('reason')]:
        return ResponseMessage("Required parameters not supplied.", 400)
    if(params['status'].lower() not in ('canceled', 'pending', 'rejected', 'accepted')):
        return ResponseMessage("Invalid status field. Must be ('canceled', 'pending', 'rejected', 'accepted')", 400)
    if(len(params['reason']) == 0):
        return ResponseMessage("Reason must be non-empty.", 400)

    try:
        result = db.session.execute(text("SELECT * FROM patients WHERE patient_id = :patient_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid patient id.", 400)
        result = db.session.execute(text("SELECT * FROM doctors WHERE doctor_id = :doctor_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid doctor id.", 400)
        result = db.session.execute(text("SELECT start_time, end_time FROM appointments WHERE doctor_id = :doctor_id"), params)
        startA = request.json.get('start_time')
        endA = end_time
        for times in result:
            if (startA < times.end_time) and (times.start_time < endA):
                return ResponseMessage("Invalid timeslot.", 400)
        #execute query
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Error Executing Query:\n{e}", 500)
    else:
        db.session.commit()
        return ResponseMessage(f"Appointment entry successfully created (id: {params['appointment_id']})", 201)

@app.route("/appointments/<int:appointment_id>", methods=['PATCH'])
@login_required
@swag_from("docs/appointments/patch.yml")
def update_appointment(appointment_id):
    #sql query
    query = text(f"""
        UPDATE appointments SET
            doctor_id = {':doctor_id' if request.json.get('doctor_id') != None else 'doctor_id'},
            patient_id = {':patient_id' if request.json.get('patient_id') != None else 'patient_id'},
            start_time = {':start_time' if request.json.get('start_time') != None else 'start_time'},
            status = {':status' if request.json.get('status') != None else 'status'},
            location = {':location' if request.json.get('location') != None else 'location'},
            reason = {':reason' if request.json.get('reason') != None else 'reason'},
            notes = {':notes' if request.json.get('notes') != None else 'notes'},
            details = {':details' if request.json.get('details') != None else 'details'}
        WHERE appointment_id = :appointment_id
    """)
    location = request.json.get('location')
    if location is None:
        location = ""
    details = request.json.get('details')
    if details is None:
        details = ""
    notes = request.json.get('notes')
    if notes is None:
        notes = ""

    valid_datetime = r"^\d{4}-\d{2}-\d{2} [0-5][0-9]:[0-5][0-9]:[0-5][0-9]$"
    if(request.json.get('start_time') != None and re.search(valid_datetime, request.json.get('start_time')) == None):
        return ResponseMessage("Invalid Start Time. Format: (yyyy-mm-dd hh:mm:ss)", 400)
    if (request.json.get('start_time') != None):
        end_time = datetime.strptime(request.json.get('start_time'), "%Y-%m-%d %H:%M:%S")
        end_time = end_time + timedelta(hours=1)
        end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        end_time_result = db.session.execute(text("SELECT end_time FROM appointments WHERE appointment_id = :appointment_id"),{"appointment_id": appointment_id}).first()
        end_time = end_time_result.end_time if end_time_result else None
        
    params = {
        'appointment_id': appointment_id,
        'doctor_id': request.json.get('doctor_id'),
        'patient_id': request.json.get('patient_id'),
        'start_time': request.json.get('start_time'),
        'end_time': end_time,
        'status': request.json.get('status'),
        'location': location,
        'reason': request.json.get('reason'),
        'details': details,
        'reason': request.json.get('reason'),
        'notes': notes
    }
    #input validation
    if(db.session.execute(text("SELECT * FROM appointments WHERE appointment_id = :appointment_id"), params).first() == None):
        return ResponseMessage("Appointment not found.", 404)
    if all(param == None for param in list(params.values())[1:]):
        return ResponseMessage("No parameters were passed to update...", 200)
    if(params['status'] != None and params['status'].lower() not in ('canceled', 'pending', 'rejected', 'accepted')):
        return ResponseMessage("Invalid status field. Must be ('canceled', 'pending', 'rejected', 'accepted')", 400)
    if(params['reason'] != None and len(params['reason']) == 0):
        return ResponseMessage("Reason must be non-empty.", 400)
    #add appointment time validation
    if(params['start_time'] != None and re.search(valid_datetime, params['start_time']) == None):
        return ResponseMessage("Invalid Start Time. Format: (yyyy-mm-dd hh:mm:ss)", 400)
      
    if (request.json.get('start_time') != None):
        result = db.session.execute(text("SELECT start_time, end_time FROM appointments WHERE doctor_id = :doctor_id"), params)
        startA = request.json.get('start_time')
        endA = end_time
        for times in result:
            if (startA < times.end_time) and (times.start_time < endA):
                return ResponseMessage("Invalid timeslot.", 400)
        
    if(params['doctor_id'] != None and db.session.execute(text("SELECT * FROM doctors WHERE doctor_id = :doctor_id"), params).first() == None):
        return ResponseMessage("Invalid doctor ID.", 400)
    if(params['patient_id'] != None and db.session.execute(text("SELECT * FROM patients WHERE patient_id = :patient_id"), params).first() == None):
        return ResponseMessage("Invalid patient ID.", 400)
    try:
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Server/SQL Error. Exeption: \n{e}", 500)
    else:
        db.session.commit()
        return ResponseMessage("Appointment Successfully Updated.", 200) 

@app.route("/patient_progress", methods=['GET'])
@login_required
@swag_from('docs/patientprogress/get.yml')
def get_patient_progress():
    #sql query
    query = "SELECT * FROM patient_progress\n"
    #get inputs
    params = {
        'progid': "" if request.args.get('progress_id') == None else request.args.get('progress_id'),
        'pid': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'datetime': "" if request.args.get('date_logged') == None else '%' + request.args.get('date_logged') + '%'
    }
    if(params['progid'] != "" or params['pid'] != "" or params['datetime'] != ""):
        query += ("WHERE " + ("progress_id = :progid\n" if params['progid'] != "" else "TRUE\n"))
        query += ("AND " + ("patient_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("date_logged LIKE :datetime\n" if params['datetime'] != "" else "TRUE\n"))
    query += ("ORDER BY date_logged DESC\n")
    #execute query
    result = db.session.execute(text(query), params)
    json = {'patient_progress': []}
    for row in result:
        json['patient_progress'].append({
            'progress_id': row.progress_id,
            'patient_id': row.patient_id,
            'weight': row.weight,
            'weight_goal': row.weight_goal,
            'calories': row.calories,
            'notes': row.notes,
            'date_logged': row.date_logged
        })
    return json, 200

@app.route("/patient_progress/<int:progress_id>", methods=['DELETE'])
@login_required
@swag_from('docs/patientprogress/delete.yml')
def delete_patient_progress(progress_id):
    try:
        result = db.session.execute(text("SELECT * FROM patient_progress WHERE progress_id = :progress_id\n"), {'progress_id': progress_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM patient_progress WHERE progress_id = :progress_id\n"), {'progress_id': progress_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/patient_progress", methods=['POST'])
@login_required
@swag_from('docs/patientprogress/post.yml')
def add_patient_progress():
    #sql query
    query = text("""
        INSERT INTO patient_progress (progress_id, patient_id, weight, weight_goal, calories, notes, date_logged)
        VALUES (
            :progress_id,
            :patient_id,
            :weight,
            :weight_goal,
            :calories,
            :notes,
            CURRENT_TIMESTAMP
            )
    """)
    # NOTE: doing progress_id this way could bring about a race condition.... but lets be real this is never happening.
    params = {
        'progress_id': (db.session.execute(text("SELECT MAX(progress_id) + 1 AS progress_id FROM patient_progress")).first()).progress_id,
        'patient_id': request.json.get('patient_id'),
        'weight': request.json.get('weight'),
        'calories': request.json.get('calories'),
        'weight_goal': request.json.get('weight_goal'),
        'notes': request.json.get('notes')
    }
    #input validation
    if None in list(params.values())[:-1]:
        return ResponseMessage("Required parameters not supplied.", 400)
    try:
        result = db.session.execute(text("SELECT * FROM patients WHERE patient_id = :patient_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid patient id.", 400)
        if(request.json.get('weight') <= 0 or request.json.get('weight') >= 1500):
            return ResponseMessage("Invalid weight.", 400)
        if(request.json.get('weight_goal') <= 0 or request.json.get('weight_goal') >= 1500):
            return ResponseMessage("Invalid weight goal.", 400)
        if(request.json.get('calories') <= 0 or request.json.get('calories') >= 30000):
            return ResponseMessage("Invalid calories.", 400)
        #execute query
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Error Executing Query:\n{e}", 500)
    else:
        db.session.commit()
        return ResponseMessage(f"patient progress entry successfully created (id: {params['progress_id']})", 201)

@app.route("/patient_exercise_assignments", methods=['GET'])
@login_required
@swag_from('docs/patientexerciseassignments/get.yml')
def get_patient_exercise_assignments():
    #sql query
    query = "SELECT * FROM patient_exercise_assignments\n"
    #get inputs
    params = {
        'aid': "" if request.args.get('assignment_id') == None else request.args.get('assignment_id'),
        'pid': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'did': "" if request.args.get('doctor_id') == None else request.args.get('doctor_id'),
        'eid': "" if request.args.get('exercise_id') == None else request.args.get('exercise_id'),
        'date': "" if request.args.get('assigned_at') == None else '%' + request.args.get('assigned_at') + '%'
    }
    if(params['aid'] != "" or params['pid'] != "" or params['did'] != "" or params['eid'] != "" or params['date'] != ""):
        query += ("WHERE " + ("assignment_id = :aid\n" if params['aid'] != "" else "TRUE\n"))
        query += ("AND " + ("patient_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("doctor_id = :did\n" if params['did'] != "" else "TRUE\n"))
        query += ("AND " + ("exercise_id = :eid\n" if params['eid'] != "" else "TRUE\n"))
        query += ("AND " + ("assigned_at LIKE :date\n" if params['date'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'patient_exercise_assignments': []}
    for row in result:
        json['patient_exercise_assignments'].append({
            'assignment_id': row.assignment_id,
            'patient_id': row.patient_id,
            'doctor_id': row.doctor_id,
            'exercise_id': row.exercise_id,
            'frequency_per_week': row.frequency_per_week,
            'reps': row.reps,
            'sets': row.sets,
            'assigned_at': row.assigned_at
        })
    return json, 200

@app.route("/patient_exercise_assignments/<int:assignment_id>", methods=['PATCH'])
@swag_from('docs/patientexerciseassignments/patch.yml')
def patch_patient_exercise_assignments(assignment_id):
    data = request.get_json(force=True)
    
    existing = db.session.execute(
        text("SELECT * FROM patient_exercise_assignments WHERE assignment_id = :assignment_id"),
        {'assignment_id': assignment_id}
    ).first()
    
    if not existing:
        return {"error": "Patient exercise assignment not found"}, 404

    update_fields = []
    params = {}
    
    if 'patient_id' in data:
        update_fields.append("patient_id = :patient_id")
        params['patient_id'] = data['patient_id']
    if 'doctor_id' in data:
        update_fields.append("doctor_id = :doctor_id")
        params['doctor_id'] = data['doctor_id']
    if 'exercise_id' in data:
        update_fields.append("exercise_id = :exercise_id")
        params['exercise_id'] = data['exercise_id']
    if 'frequency_per_week' in data:
        update_fields.append("frequency_per_week = :frequency_per_week")
        params['frequency_per_week'] = data['frequency_per_week']
    if 'reps' in data:
        update_fields.append("reps = :reps")
        params['reps'] = data['reps']
    if 'sets' in data:
        update_fields.append("sets = :sets")
        params['sets'] = data['sets']
    
    if not update_fields:
        return {"error": "No update fields provided."}, 400

    params['assignment_id'] = assignment_id
    query = "UPDATE patient_exercise_assignments SET " + ", ".join(update_fields) + " WHERE assignment_id = :assignment_id"
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error updating patient exercise assignment"}, 500

    return {"message": "Patient exercise assignment updated successfully"}, 200


@app.route("/patient_exercise_assignments", methods=['POST'])
@swag_from('docs/patientexerciseassignments/post.yml')
def post_patient_exercise_assignments():
    data = request.get_json(force=True)
    
    if 'patient_id' not in data or 'doctor_id' not in data or 'exercise_id' not in data:
        return {"error": "Missing required fields: patient_id, doctor_id, and exercise_id"}, 400

    from datetime import datetime
    query = """
        INSERT INTO patient_exercise_assignments (patient_id, doctor_id, exercise_id, frequency_per_week, reps, sets, assigned_at)
        VALUES (:patient_id, :doctor_id, :exercise_id, :frequency_per_week, :reps, :sets, :assigned_at)
    """
    params = {
        'patient_id': data['patient_id'],
        'doctor_id': data['doctor_id'],
        'exercise_id': data['exercise_id'],
        'frequency_per_week': data['frequency_per_week'],
        'reps': data['reps'],
        'sets': data['sets'],
        'assigned_at': datetime.utcnow()
    }
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error creating patient exercise assignment"}, 500

    return {"message": "Patient exercise assignment created successfully"}, 201


@app.route("/patient_exercise_assignments/<int:assignment_id>", methods=['DELETE'])
@login_required
@swag_from('docs/patientexerciseassignments/delete.yml')
def delete_patient_exercise_assignments(assignment_id):
    try:
        result = db.session.execute(text("SELECT * FROM patient_exercise_assignments WHERE assignment_id = :assignment_id\n"), {'assignment_id': assignment_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM patient_exercise_assignments WHERE assignment_id = :assignment_id\n"), {'assignment_id': assignment_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/medications", methods=['GET'])
@swag_from('docs/medications/get.yml')
def get_medications():
    #sql query
    query = "SELECT * FROM medications\n"
    #get inputs
    params = {
        'mid': "" if request.args.get('medication_id') == None else request.args.get('medication_id'),
        'name': "" if request.args.get('name') == None else '%' + request.args.get('name') + '%'
    }
    if(params['mid'] != "" or params['name'] != ""):
        query += ("WHERE " + ("medication_id = :mid\n" if params['mid'] != "" else "TRUE\n"))
        query += ("AND " + ("name LIKE :name\n" if params['name'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'medications': []}
    for row in result:
        json['medications'].append({
            'medication_id': row.medication_id,
            'name': row.name,
            'description': row.description
        })
    return json, 200

@app.route("/medications/<int:medication_id>", methods=['DELETE'])
@swag_from('docs/medications/delete.yml')
def delete_medications(medication_id):
    try:
        result = db.session.execute(text("SELECT * FROM medications WHERE medication_id = :medication_id\n"), {'medication_id': medication_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM medications WHERE medication_id = :medication_id\n"), {'medication_id': medication_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/inventory", methods=['GET'])
@swag_from('docs/inventory/get.yml')
def get_inventory():
    #sql query
    query = "SELECT * FROM inventory\n"
    #get inputs
    params = {
        'iid': "" if request.args.get('inventory_id') == None else request.args.get('inventory_id'),
        'mid': "" if request.args.get('medication_id') == None else request.args.get('medication_id'),
    }
    if(params['iid'] != "" or params['mid'] != ""):
        query += ("WHERE " + ("inventory_id = :iid\n" if params['iid'] != "" else "TRUE\n"))
        query += ("AND " + ("medication_id = :mid\n" if params['mid'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'inventory': []}
    for row in result:
        json['inventory'].append({
            'inventory_id': row.inventory_id,
            'medication_id': row.medication_id,
            'stock': row.stock,
            'last_updated': row.last_updated
        })
    return json, 200

@app.route("/inventory/<int:inventory_id>", methods=['DELETE'])
@swag_from('docs/inventory/delete.yml')
def delete_inventory(inventory_id):
    try:
        result = db.session.execute(text("SELECT * FROM inventory WHERE inventory_id = :inventory_id\n"), {'inventory_id': inventory_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM inventory WHERE inventory_id = :inventory_id\n"), {'inventory_id': inventory_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/exercise_plans", methods=['GET'])
@login_required
@swag_from('docs/exerciseplans/get.yml')
def get_exercise_plans():
    #sql query
    query = "SELECT * FROM exercise_plans\n"
    #get inputs
    params = {
        'eid': "" if request.args.get('exercise_id') == None else request.args.get('exercise_id'),
        'tit': "" if request.args.get('title') == None else '%' + request.args.get('title') + '%', # haha Tity
    }
    if(params['eid'] != "" or params['tit'] != ""):
        query += ("WHERE " + ("exercise_id = :eid\n" if params['eid'] != "" else "TRUE\n"))
        query += ("AND " + ("title LIKE :tit\n" if params['tit'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'exercise_plans': []}
    for row in result:
        json['exercise_plans'].append({
            'exercise_id': row.exercise_id,
            'title': row.title,
            'description': row.description
        })
    return json, 200

@app.route("/exercise_plans/<int:exercise_id>", methods=['DELETE'])
@login_required
@swag_from('docs/exerciseplans/delete.yml')
def delete_exercise_plans(exercise_id):
    try:
        result = db.session.execute(text("SELECT * FROM exercise_plans WHERE exercise_id = :exercise_id\n"), {'exercise_id': exercise_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM exercise_plans WHERE exercise_id = :exercise_id\n"), {'exercise_id': exercise_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/doctor_patient_relationship", methods=['GET'])
@swag_from('docs/doctorpatientrelationship/get.yml')
def get_doctor_patient_relationship():
    #sql query
    query = "SELECT * FROM doctor_patient_relationship\n"
    #get inputs
    params = {
        'did': "" if request.args.get('doctor_id') == None else request.args.get('doctor_id'),
        'pid': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'status': "" if request.args.get('status') == None else request.args.get('status'),
    }
    if(params['did'] != "" or params['pid'] != "" or params['status'] != ""):
        query += ("WHERE " + ("doctor_id = :did\n" if params['did'] != "" else "TRUE\n"))
        query += ("AND " + ("patient_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("status LIKE :status\n" if params['status'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'doctor_patient_relationship': []}
    for row in result:
        json['doctor_patient_relationship'].append({
            'doctor_id': row.doctor_id,
            'patient_id': row.patient_id,
            'status': row.status,
            'date_assigned': row.date_assigned
        })
    return json, 200

@app.route("/doctor_patient_relationship/<int:doctor_id>/<int:patient_id>", methods=['DELETE'])
@swag_from('docs/doctorpatientrelationship/delete.yml')
def delete_doctor_patient_relationship(doctor_id, patient_id):
    try:
        result = db.session.execute(text("SELECT * FROM doctor_patient_relationship WHERE doctor_id = :doctor_id AND patient_id = :patient_id\n"), {'doctor_id': doctor_id, 'patient_id': patient_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM doctor_patient_relationship WHERE doctor_id = :doctor_id AND patient_id = :patient_id\n"), {'doctor_id': doctor_id, 'patient_id': patient_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)
    
from datetime import datetime

@app.route("/doctor_patient_relationship/<int:doctor_id>/<int:patient_id>", methods=['PATCH'])
@swag_from('docs/doctorpatientrelationship/patch.yml')
def patch_doctor_patient_relationship(doctor_id, patient_id):
    data = request.get_json(force=True)
    
    # Check if the relationship exists.
    existing = db.session.execute(
        text("SELECT * FROM doctor_patient_relationship WHERE doctor_id = :doctor_id AND patient_id = :patient_id"),
        {'doctor_id': doctor_id, 'patient_id': patient_id}
    ).first()
    
    if not existing:
        return {"error": "Doctor patient relationship not found"}, 404

    update_fields = []
    params = {}
    
    # Allow updating status only.
    if 'status' in data:
        if not data['status'].strip():
            return {"error": "Status cannot be empty."}, 400
        update_fields.append("status = :status")
        params['status'] = data['status']
    
    # Ensure at least one updatable field (other than date_assigned) is provided.
    if not update_fields:
        return {"error": "No update fields provided."}, 400

    # Automatically update date_assigned to current date and time.
    update_fields.append("date_assigned = :date_assigned")
    params['date_assigned'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    params['doctor_id'] = doctor_id
    params['patient_id'] = patient_id
    
    query = (
        "UPDATE doctor_patient_relationship SET " +
        ", ".join(update_fields) +
        " WHERE doctor_id = :doctor_id AND patient_id = :patient_id"
    )
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error updating doctor patient relationship"}, 500
    
    return {"message": "Doctor patient relationship updated successfully"}, 200

@app.route("/doctor_patient_relationship", methods=['POST'])
@swag_from('docs/doctorpatientrelationship/post.yml')
def post_doctor_patient_relationship():
    data = request.get_json(force=True)
    
    # Validate required fields
    if 'doctor_id' not in data or 'patient_id' not in data or 'status' not in data:
        return {"error": "Missing required fields: doctor_id, patient_id, and status"}, 400
    if not str(data['status']).strip():
        return {"error": "Status cannot be empty"}, 400

    from datetime import datetime
    query = """
        INSERT INTO doctor_patient_relationship (doctor_id, patient_id, status, date_assigned)
        VALUES (:doctor_id, :patient_id, :status, :date_assigned)
    """
    params = {
        'doctor_id': data['doctor_id'],
        'patient_id': data['patient_id'],
        'status': data['status'],
        # Automatically set date_assigned to the current date and time
        'date_assigned': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error creating doctor patient relationship"}, 500
    
    return {"message": "Doctor patient relationship created successfully"}, 201



@app.route("/credit_card", methods=['GET'])
@swag_from('docs/creditcard/get.yml')
def get_credit_card():
    #sql query
    query = "SELECT * FROM credit_card\n"
    #get inputs
    params = {
        'cid': "" if request.args.get('creditcard_id') == None else request.args.get('creditcard_id'),
        'cnum': "" if request.args.get('card_ending') == None else '%' + request.args.get('card_ending'),
        'exp': "" if request.args.get('exp_date') == None else '%' + request.args.get('exp_date') + '%',
    }
    if(len(params['cnum'][1:]) > 4):
        return {'message': "Card ending query cannot exceed 4 characters for security purposes. Please use creditcard_id instead."}, 400
    if(params['cid'] != "" or params['cnum'] != "" or params['exp'] != ""):
        query += ("WHERE " + ("creditcard_id = :cid\n" if params['cid'] != "" else "TRUE\n"))
        query += ("AND " + ("cardnumber LIKE :cnum\n" if params['cnum'] != "" else "TRUE\n"))
        query += ("AND " + ("exp_date LIKE :exp\n" if params['exp'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'credit_card': []}
    for row in result:
        json['credit_card'].append({
            'creditcard_id': row.creditcard_id,
            'card_ending': "x" + str(row.cardnumber)[-4:],
            #'cvv': row.cvv, # Nope
            'exp_date': row.exp_date
        })
    return json, 200

@app.route("/credit_card/<int:creditcard_id>", methods=['DELETE'])
@swag_from('docs/creditcard/delete.yml')
def delete_credit_card(creditcard_id):
    try:
        result = db.session.execute(text("SELECT * FROM credit_card WHERE creditcard_id = :creditcard_id\n"), {'creditcard_id': creditcard_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM credit_card WHERE creditcard_id = :creditcard_id\n"), {'creditcard_id': creditcard_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)
    
valid_cardnum = r"^\d{14,18}$"
valid_cvv = r"^\d{3}$"
valid_date = r"^\d{4}-\d{2}-\d{2}$"

@app.route("/credit_card/<int:creditcard_id>", methods=['PATCH'])
@swag_from('docs/creditcard/patch.yml')
def patch_credit_card(creditcard_id):
    data = request.get_json(force=True)
    
    if 'cardnumber' in data:
        if not re.match(valid_cardnum, data['cardnumber']):
            return {"error": "Invalid card number format. It must contain between 14 and 18 digits."}, 400
    
    if 'exp_date' in data:
        if not re.match(valid_date, data['exp_date']):
            return {"error": "Invalid expiration date format. Expected YYYY-MM-DD."}, 400
    
    if 'cvv' in data:
        if not re.match(valid_cvv, data['cvv']):
            return {"error": "Invalid CVV format. It must be exactly 3 digits."}, 400

    existing = db.session.execute(
        text("SELECT * FROM credit_card WHERE creditcard_id = :creditcard_id"),
        {'creditcard_id': creditcard_id}
    ).first()
    
    if not existing:
        return {"error": "Credit card not found"}, 404

    update_fields = []
    params = {}
    
    if 'cardnumber' in data:
        update_fields.append("cardnumber = :cardnumber")
        params['cardnumber'] = data['cardnumber']
    if 'exp_date' in data:
        update_fields.append("exp_date = :exp_date")
        params['exp_date'] = data['exp_date']
    if 'cvv' in data:
        update_fields.append("cvv = :cvv")
        params['cvv'] = data['cvv']
    
    if not update_fields:
        return {"error": "No update fields provided."}, 400

    params['creditcard_id'] = creditcard_id
    query = "UPDATE credit_card SET " + ", ".join(update_fields) + " WHERE creditcard_id = :creditcard_id"
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error updating credit card"}, 500

    return {"message": "Credit card updated successfully"}, 200



@app.route("/address", methods=['GET'])
@swag_from('docs/address/get.yml')
def get_address():
    #sql query
    query = "SELECT * FROM address\n"
    #get inputs
    params = {
        'aid': "" if request.args.get('address_id') == None else request.args.get('address_id'),
        'zip': "" if request.args.get('zip') == None else request.args.get('zip'),
        'city': "" if request.args.get('city') == None else '%' + request.args.get('city') + '%',
        'addr': "" if request.args.get('address') == None else '%' + request.args.get('address') + '%',
        'addr2': "" if request.args.get('address2') == None else '%' + request.args.get('address2') + '%',
        'state': "" if request.args.get('state') == None else request.args.get('state'),
    }
    if(params['aid'] != "" or params['zip'] != "" or params['city'] != "" or params['addr'] != "" or params['addr2'] != ""):
        query += ("WHERE " + ("address_id = :aid\n" if params['aid'] != "" else "TRUE\n"))
        query += ("AND " + ("zip = :zip\n" if params['zip'] != "" else "TRUE\n"))
        query += ("AND " + ("state = :state\n" if params['state'] != "" else "TRUE\n"))
        query += ("AND " + ("city LIKE :city\n" if params['city'] != "" else "TRUE\n"))
        query += ("AND " + ("address LIKE :addr\n" if params['addr'] != "" else "TRUE\n"))
        query += ("AND " + ("address2 LIKE :addr2\n" if params['addr2'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'address': []}
    for row in result:
        json['address'].append({
            'address_id': row.address_id,
            'city': row.city,
            'country': row.country,
            'address2': row.address2,
            'address': row.address,
            'state': row.state,
            'zip': str(row.zip).zfill(5)
        })
    return json, 200

@app.route("/address/<int:address_id>", methods=['DELETE'])
@swag_from('docs/address/delete.yml')
def delete_address(address_id):
    try:
        result = db.session.execute(text("SELECT * FROM address WHERE address_id = :address_id\n"), {'address_id': address_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM address WHERE address_id = :address_id\n"), {'address_id': address_id})
        else:
            print(result.first())
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)
    
@app.route("/address/<int:address_id>", methods=['PATCH'])
@swag_from('docs/address/patch.yml')
def patch_address(address_id):
    data = request.get_json(force=True)
    
    # Check if the address exists first
    existing = db.session.execute(
        text("SELECT * FROM address WHERE address_id = :address_id"),
        {'address_id': address_id}
    ).first()
    
    if not existing:
        return {"error": "Address not found"}, 404

    update_fields = []
    params = {}
    
    if 'city' in data:
        update_fields.append("city = :city")
        params['city'] = data['city']
    if 'country' in data:
        update_fields.append("country = :country")
        params['country'] = data['country']
    if 'address' in data:
        update_fields.append("address = :address")
        params['address'] = data['address']
    if 'zip' in data:
        update_fields.append("zip = :zip")
        params['zip'] = data['zip']
    if 'address2' in data:
        update_fields.append("address2 = :address2")
        params['address2'] = data['address2']
    
    if not update_fields:
        return {"error": "No update fields provided."}, 400

    params['address_id'] = address_id
    query = "UPDATE address SET " + ", ".join(update_fields) + " WHERE address_id = :address_id"
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error updating address"}, 500

    return {"message": "Address updated successfully"}, 200




@app.route("/pharmacists", methods=['GET'])
@swag_from('docs/pharmacists/get.yml')
def get_pharmacists():
    #sql query
    query = "SELECT * FROM pharmacists\n"
    #get inputs
    params = {
        'pid': "" if request.args.get('pharmacist_id') == None else request.args.get('pharmacist_id'),
        'loc': "" if request.args.get('pharmacy_location') == None else '%' + request.args.get('pharmacy_location') + '%',
    }
    if(params['pid'] != "" or params['loc'] != ""):
        query += ("WHERE " + ("pharmacist_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("pharmacy_location LIKE :loc\n" if params['loc'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'pharmacists': []}
    for row in result:
        json['pharmacists'].append({
            'pharmacist_id': row.pharmacist_id,
            'pharmacy_location': row.pharmacy_location,
        })
    return json, 200

@app.route("/pharmacists/<int:pharmacist_id>", methods=['DELETE'])
@swag_from('docs/pharmacists/delete.yml')
def delete_pharmacists(pharmacist_id):
    try:
        result = db.session.execute(text("SELECT * FROM pharmacists WHERE pharmacist_id = :pharmacist_id\n"), {'pharmacist_id': pharmacist_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM pharmacists WHERE pharmacist_id = :pharmacist_id\n"), {'pharmacist_id': pharmacist_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/forum_comments", methods=['GET'])
@swag_from('docs/forumcomments/get.yml')
def get_forum_comments():
    #sql query
    query = "SELECT * FROM forum_comments AS F JOIN users AS U ON F.user_id = U.user_id\n"
    #get inputs
    params = {
        'cid': "" if request.args.get('comment_id') == None else request.args.get('comment_id'),
        'pid': "" if request.args.get('post_id') == None else request.args.get('post_id'),
        'uid': "" if request.args.get('user_id') == None else request.args.get('user_id'),
    }
    if(params['pid'] != "" or params['uid'] != "" or params['cid'] != ""):
        query += ("WHERE " + ("post_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("user_id = :uid\n" if params['uid'] != "" else "TRUE\n"))
        query += ("AND " + ("comment_id = :cid\n" if params['cid'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'forum_comments': []}
    for row in result:
        json['forum_comments'].append({
            'comment_id': row.comment_id,
            'post_id': row.post_id,
            'user_id': row.user_id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'comment_text': row.comment_text,
            'created_at': row.created_at
        })
    return json, 200

@app.route("/forum_comments/<int:comment_id>", methods=['DELETE'])
@swag_from('docs/forumcomments/delete.yml')
def delete_forum_comments(comment_id):
    try:
        result = db.session.execute(text("SELECT * FROM forum_comments WHERE comment_id = :comment_id\n"), {'comment_id': comment_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM forum_comments WHERE comment_id = :comment_id\n"), {'comment_id': comment_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/forum_comments", methods=['POST'])
@swag_from('docs/forumcomments/post.yml')
def add_forum_comments():
    #sql query
    query = text("""
        INSERT INTO forum_comments (comment_id, post_id, user_id, comment_text, created_at)
        VALUES (
            :comment_id,
            :post_id,
            :user_id,
            :comment_text,
            CURRENT_TIMESTAMP
            )
    """)
    # NOTE: doing comment_id this way could bring about a race condition.... but lets be real this is never happening.
    params = {
        'comment_id': (db.session.execute(text("SELECT MAX(comment_id) + 1 AS comment_id FROM forum_comments")).first()).comment_id,
        'post_id': request.json.get('post_id'),
        'user_id': request.json.get('user_id'),
        'comment_text': request.json.get('comment_text')
    }
    #input validation
    if None in list(params.values())[:-1]:
        return ResponseMessage("Required parameters not supplied.", 400)
    try:
        result = db.session.execute(text("SELECT * FROM forum_posts WHERE post_id = :post_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid post id.", 400)
        result = db.session.execute(text("SELECT * FROM users WHERE user_id = :user_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid user id.", 400)
        if(len(str(request.json.get('comment_text'))) <= 0):
            return ResponseMessage("Invalid comment text.", 400)
        #execute query
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Error Executing Query:\n{e}", 500)
    else:
        db.session.commit()
        return ResponseMessage(f"comment entry successfully created (id: {params['comment_id']})", 201)

@app.route("/forum_comments/<int:comment_id>", methods=['PATCH'])
@swag_from('docs/forumcomments/patch.yml')
def patch_forum_comments(comment_id):
    data = request.get_json(force=True)
    
    existing = db.session.execute(
        text("SELECT * FROM forum_comments WHERE comment_id = :comment_id"),
        {'comment_id': comment_id}
    ).first()
    
    if not existing:
        return {"error": "Comment not found"}, 404
    
    update_fields = []
    params = {}
    
    if 'comment_text' in data:
        if not data['comment_text'].strip():
            return {"error": "comment_text cannot be empty."}, 400
        update_fields.append("comment_text = :comment_text")
        params['comment_text'] = data['comment_text']
    
    if not update_fields:
        return {"error": "No update fields provided."}, 400
    
    params['comment_id'] = comment_id
    query = "UPDATE forum_comments SET " + ", ".join(update_fields) + " WHERE comment_id = :comment_id"
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error updating comment"}, 500
    
    return {"message": "Comment updated successfully"}, 200


@app.route("/forum_posts", methods=['GET'])
@swag_from('docs/forumposts/get.yml')
def get_forum_posts():
    #sql query
    query = "SELECT F.post_id, U.user_id, U.first_name, U.last_name, F.title, F.content, F.post_type, F.created_at AS post_created_at FROM forum_posts AS F JOIN users AS U ON F.user_id = U.user_id\n"
    #get inputs
    params = {
        'pid': "" if request.args.get('post_id') == None else request.args.get('post_id'),
        'uid': "" if request.args.get('user_id') == None else request.args.get('user_id'),
        'title': "" if request.args.get('title') == None else '%' + request.args.get('title') + '%',
        'type': "" if request.args.get('post_type') == None else '%' + request.args.get('post_type') + '%',
        'order_by': "DESC" if request.args.get('order_by') == None else request.args.get('order_by')
    }
    if(params['pid'] != "" or params['uid'] != "" or params['title'] != "" or params['type'] != "" or params['order_by'] != ""):
        query += ("WHERE " + ("post_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("user_id = :uid\n" if params['uid'] != "" else "TRUE\n"))
        query += ("AND " + ("title LIKE :title\n" if params['title'] != "" else "TRUE\n"))
        query += ("AND " + ("post_type LIKE :type\n" if params['type'] != "" else "TRUE\n"))
        query += (f"ORDER BY F.created_at {"ASC" if params['order_by'].upper() == "ASC" else "DESC"}")
        print(query)
    #execute query
    result = db.session.execute(text(query), params)
    json = {'forum_posts': []}
    for row in result:
        json['forum_posts'].append({
            'post_id': row.post_id,
            'user_id': row.user_id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'title': row.title,
            'content': row.content,
            'post_type': row.post_type,
            'created_at': row.post_created_at
        })
    return json, 200

@app.route("/forum_posts", methods=['POST'])
@swag_from('docs/forumposts/post.yml')
def add_forum_posts():
    #sql query
    query = text("""
        INSERT INTO forum_posts (post_id, user_id, title, content, post_type, created_at)
        VALUES (
            :post_id,
            :user_id,
            :title,
            :content,
            :post_type,
            CURRENT_TIMESTAMP
            )
    """)
    # NOTE: doing comment_id this way could bring about a race condition.... but lets be real this is never happening.
    params = {
        'post_id': (db.session.execute(text("SELECT MAX(post_id) + 1 AS post_id FROM forum_posts")).first()).post_id,
        'user_id': request.json.get('user_id'),
        'title': request.json.get('title'),
        'content': request.json.get('content'),
        'post_type': request.json.get('post_type')
    }
    #input validation
    if None in list(params.values())[:-1]:
        return ResponseMessage("Required parameters not supplied.", 400)
    try:
        result = db.session.execute(text("SELECT * FROM users WHERE user_id = :user_id"), params)
        if(result.first() == None):
            return ResponseMessage("Invalid user_id.", 400)
        if (request.json.get('post_type').lower() != "discussion" and request.json.get('post_type').lower() != "exercise plan"):
            return ResponseMessage("Invalid post_type.", 400)
        if(len(str(request.json.get('comment_text'))) <= 0):
            return ResponseMessage("Invalid comment text.", 400)
        #execute query
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Error Executing Query:\n{e}", 500)
    else:
        db.session.commit()
        data = {
            'message': 'post entry successfully created',
            'id': params['post_id']
        }
        return jsonify(data), 201

@app.route("/forum_posts/<int:post_id>", methods=['DELETE'])
@swag_from('docs/forumposts/delete.yml')
def delete_forum_posts(post_id):
    try:
        result = db.session.execute(text("SELECT * FROM forum_posts WHERE post_id = :post_id\n"), {'post_id': post_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM forum_posts WHERE post_id = :post_id\n"), {'post_id': post_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/forum_posts/<int:post_id>", methods=['PATCH'])
@swag_from('docs/forumposts/patch.yml')
def update_forum_posts(post_id):
        #sql query
    query = text(f"""
        UPDATE forum_posts SET
            title = {':title' if request.json.get('title') != None else 'title'},
            content = {':content' if request.json.get('content') != None else 'content'},
            post_type = {':post_type' if request.json.get('post_type') != None else 'post_type'}
        WHERE post_id = :post_id
    """)
    params = {
        'post_id': post_id,
        'title': request.json.get('title'),
        'content': request.json.get('content'),
        'post_type': request.json.get('post_type')
    }
    #input validation
    if(db.session.execute(text("SELECT * FROM forum_posts WHERE post_id = :post_id"), params).first() == None):
        return ResponseMessage("post not found.", 404)
    if (request.json.get('post_type').lower() != "discussion" and request.json.get('post_type').lower() != "exercise plan"):
        return ResponseMessage("Invalid post_type.", 400)
    if(len(str(request.json.get('comment_text'))) <= 0):
        return ResponseMessage("Invalid comment text.", 400)
    try:
        db.session.execute(query, params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Server/SQL Error. Exeption: \n{e}", 500)
    else:
        db.session.commit()
        return ResponseMessage("Post Successfully Updated.", 200) 

@app.route("/reviews", methods=['GET'])
@swag_from('docs/reviews/get.yml')
def get_reviews():
    #sql query
    query = "SELECT * FROM reviews\n"
    
    #get inputs
    params = {
        'rid': "" if request.args.get('review_id') is None else request.args.get('review_id'),
        'did': "" if request.args.get('doctor_id') is None else request.args.get('doctor_id'),
        'pid': "" if request.args.get('patient_id') is None else request.args.get('patient_id'),
        'rating': "" if request.args.get('rating') is None else request.args.get('rating'),
        'text': "" if request.args.get('review_text') is None else '%' + request.args.get('review_text') + '%',
    }
    
    if (params['rid'] != "" or params['did'] != "" or params['pid'] != "" or params['rating'] != "" or params['text'] != ""):
        query += ("WHERE " + ("review_id = :rid\n" if params['rid'] != "" else "TRUE\n"))
        query += ("AND " + ("doctor_id = :did\n" if params['did'] != "" else "TRUE\n"))
        query += ("AND " + ("patient_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("rating = :rating\n" if params['rating'] != "" else "TRUE\n"))
        query += ("AND " + ("review_text LIKE :text\n" if params['text'] != "" else "TRUE\n"))
    
    #execute query
    result = db.session.execute(text(query), params)
    json_response = {'reviews': []}
    
    for row in result:
        json_response['reviews'].append({
            'review_id': row.review_id,
            'doctor_id': row.doctor_id,
            'patient_id': row.patient_id,
            'rating': row.rating,
            'review_text': row.review_text,
            'created_at': row.created_at
        })
    
    return json_response, 200

@app.route("/reviews", methods=['POST'])
@swag_from('docs/reviews/post.yml')
def post_review():
    data = request.get_json(force=True)
    
    # Validate required fields
    if 'patient_id' not in data or 'doctor_id' not in data or 'rating' not in data:
        return {"error": "Missing required fields: patient_id, doctor_id, and rating"}, 400
    
    from datetime import datetime
    query = """
        INSERT INTO reviews (patient_id, doctor_id, rating, review_text, created_at)
        VALUES (:patient_id, :doctor_id, :rating, :review_text, :created_at)
    """
    params = {
        'patient_id': data['patient_id'],
        'doctor_id': data['doctor_id'],
        'rating': data['rating'],
        'review_text': data.get('review_text', ""),
        'created_at': datetime.utcnow()
    }
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error creating review"}, 500

    return {"message": "Review created successfully"}, 201


@app.route("/reviews", methods=['PATCH'])
@swag_from('docs/reviews/patch.yml')
def update_review():
    data = request.get_json(force=True)
    
    if 'review_id' not in data:
        return {"error": "Missing review_id in request"}, 400
    
    # Check if the review exists
    existing_review = db.session.execute(
        text("SELECT * FROM reviews WHERE review_id = :review_id"),
        {'review_id': data['review_id']}
    ).first()
    
    if not existing_review:
        return {"error": "Review not found"}, 404
    
    update_fields = []
    params = {}
    
    if 'rating' in data:
        update_fields.append("rating = :rating")
        params['rating'] = data['rating']
    
    if 'review_text' in data:
        update_fields.append("review_text = :review_text")
        params['review_text'] = data['review_text']
    
    if not update_fields:
        return {"error": "No update fields provided."}, 400
    
    params['review_id'] = data['review_id']
    query = "UPDATE reviews SET " + ", ".join(update_fields) + " WHERE review_id = :review_id"
    
    db.session.execute(text(query), params)
    db.session.commit()
    
    return {"message": "Review updated successfully"}, 200



@app.route("/reviews/<int:review_id>", methods=['DELETE'])
@swag_from('docs/reviews/delete.yml')
def delete_reviews(review_id):
    try:
        result = db.session.execute(text("SELECT * FROM reviews WHERE review_id = :review_id\n"), {'review_id': review_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM reviews WHERE review_id = :review_id\n"), {'review_id': review_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/patients", methods=['GET'])
@swag_from('docs/patients/get.yml')
def get_patients():
    #sql query
    query = "SELECT * FROM patients\n"
    #get inputs
    params = {
        'id': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'ssn': "" if request.args.get('ssn') == None else request.args.get('ssn')
    }
    if(params['id'] != "" or params['ssn'] != ""):
        query += ("WHERE " + ("patient_id = :id\n" if params['id'] != "" else "TRUE\n"))
        query += ("AND " + ("ssn = :ssn\n" if params['ssn'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'patients': []}
    for row in result:
        json['patients'].append({
            'patient_id': row.patient_id,
            'address_id': row.address_id,
            'medical_history': row.medical_history,
            'creditcard_id': row.creditcard_id,
            'ssn': f"x{str(row.ssn)[-4:]}" # Last 4 digits for security.
        })
    return json, 200

@app.route("/patients/<int:patient_id>", methods=['DELETE'])
@swag_from('docs/patients/delete.yml')
def delete_patients(patient_id):
    try:
        result = db.session.execute(text("SELECT * FROM patients WHERE patient_id = :patient_id\n"), {'patient_id': patient_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM patients WHERE patient_id = :patient_id\n"), {'patient_id': patient_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)
    
@app.route("/patients/<int:patient_id>", methods=['PATCH'])
@swag_from('docs/patients/patch.yml')
def patch_patients(patient_id):
    data = request.get_json(force=True)
    
    # Check if the patient exists
    existing = db.session.execute(
        text("SELECT * FROM patients WHERE patient_id = :patient_id"),
        {'patient_id': patient_id}
    ).first()
    
    if not existing:
        return {"error": "Patient not found"}, 404

    update_fields = []
    params = {}
    
    if 'address_id' in data:
        update_fields.append("address_id = :address_id")
        params['address_id'] = data['address_id']
    if 'medical_history' in data:
        update_fields.append("medical_history = :medical_history")
        params['medical_history'] = data['medical_history']
    if 'creditcard_id' in data:
        update_fields.append("creditcard_id = :creditcard_id")
        params['creditcard_id'] = data['creditcard_id']
    if 'ssn' in data:
        update_fields.append("ssn = :ssn")
        params['ssn'] = data['ssn']
    
    if not update_fields:
        return {"error": "No update fields provided."}, 400

    params['patient_id'] = patient_id
    query = "UPDATE patients SET " + ", ".join(update_fields) + " WHERE patient_id = :patient_id"
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error updating patient"}, 500

    return {"message": "Patient updated successfully"}, 200


@app.route("/doctors", methods=['GET'])
@swag_from('docs/doctors/get.yml')
def get_doctors():
    #sql query
    query = "SELECT * FROM doctors\n"
    #get inputs
    params = {
        'id': "" if request.args.get('doctor_id') == None else request.args.get('doctor_id'),
        'license': "" if request.args.get('license_number') == None else request.args.get('license_number'),
        'special': "" if request.args.get('specialization') == None else '%' + request.args.get('specialization') + '%',
    }
    if(params['id'] != "" or params['license'] != "" or params['special'] != ""):
        query += ("WHERE " + ("doctor_id = :id\n" if params['id'] != "" else "TRUE\n"))
        query += ("AND " + ("license_number = :license\n" if params['license'] != "" else "TRUE\n"))
        query += ("AND " + ("specialization LIKE :special\n" if params['special'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'doctors': []}
    for row in result:
        json['doctors'].append({
            'doctor_id': row.doctor_id,
            'license_number': row.license_number,
            'specialization': row.specialization,
            'profile': row.profile
        })
    return json, 200

@app.route("/doctors/<int:doctor_id>", methods=['DELETE'])
@swag_from('docs/doctors/delete.yml')
def delete_doctors(doctor_id):
    try:
        result = db.session.execute(text("SELECT * FROM doctors WHERE doctor_id = :doctor_id\n"), {'doctor_id': doctor_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM doctors WHERE doctor_id = :doctor_id\n"), {'doctor_id': doctor_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)
    
@app.route("/doctors/<int:doctor_id>", methods=['PATCH'])
@swag_from('docs/doctors/patch.yml')
def patch_doctor(doctor_id):
    data = request.get_json(force=True)
    
    # Check if the doctor exists
    existing = db.session.execute(
        text("SELECT * FROM doctors WHERE doctor_id = :doctor_id"),
        {'doctor_id': doctor_id}
    ).first()
    
    if not existing:
        return {"error": "Doctor not found"}, 404

    update_fields = []
    params = {}
    
    if 'license_number' in data:
        update_fields.append("license_number = :license_number")
        params['license_number'] = data['license_number']
    if 'specialization' in data:
        update_fields.append("specialization = :specialization")
        params['specialization'] = data['specialization']
    if 'profile' in data:
        update_fields.append("profile = :profile")
        params['profile'] = data['profile']
    
    if not update_fields:
        return {"error": "No update fields provided."}, 400
    
    params['doctor_id'] = doctor_id
    query = "UPDATE doctors SET " + ", ".join(update_fields) + " WHERE doctor_id = :doctor_id"
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error updating doctor"}, 500

    return {"message": "Doctor updated successfully"}, 200

    
@app.route("/users", methods=['GET'])
@swag_from('docs/users/get.yml')
def get_users():
    #sql query
    query = "SELECT * FROM users\n"
    #get inputs
    params = {
        'id': "" if request.args.get('user_id') == None else request.args.get('user_id'),
        'role': "" if request.args.get('role') == None else request.args.get('role'),
        'fname': "" if request.args.get('first_name') == None else '%' + request.args.get('first_name') + '%',
        'lname': "" if request.args.get('last_name') == None else '%' + request.args.get('last_name') + '%',
        'email': "" if request.args.get('email') == None else '%' + request.args.get('email') + '%',
    }
    if(params['id'] != "" or params['role'] != "" or params['fname'] != "" or params['lname'] != "" or params['email'] != ""):
        query += ("WHERE " + ("user_id = :id\n" if params['id'] != "" else "TRUE\n"))
        query += ("AND " + ("role = :role\n" if params['role'] != "" else "TRUE\n"))
        query += ("AND " + ("first_name LIKE :fname\n" if params['fname'] != "" else "TRUE\n"))
        query += ("AND " + ("last_name LIKE :lname\n" if params['lname'] != "" else "TRUE\n"))
        query += ("AND " + ("email LIKE :email\n" if params['email'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'users': []}
    for row in result:
        json['users'].append({
            'user_id': row.user_id,
            'email': row.email,
            #'password': row.password, # Actually, maybe not.
            'first_name': row.first_name,
            'last_name': row.last_name,
            'phone_number': row.phone_number,
            'role': row.role,
            'created_at': row.created_at
        })
    return json, 200

@app.route("/users/<int:user_id>", methods=['DELETE'])
@swag_from('docs/users/delete.yml')
def delete_users(user_id):
    try:
        result = db.session.execute(text("SELECT * FROM users WHERE user_id = :user_id\n"), {'user_id': user_id})
        if result.first() != None:
            db.session.execute(text("DELETE FROM users WHERE user_id = :user_id\n"), {'user_id': user_id})
        else:
            return Response(status=400)
    except Exception as e:
        print(e)
        return Response(status=500)
    else:
        db.session.commit()
        return Response(status=200)

@app.route("/users/<int:user_id>", methods=['PATCH'])
@swag_from('docs/users/patch.yml')
def patch_user(user_id):
    data = request.get_json(force=True)
    
    # Check if the user exists
    existing = db.session.execute(
        text("SELECT * FROM users WHERE user_id = :user_id"),
        {'user_id': user_id}
    ).first()
    
    if not existing:
        return {"error": "user not found"}, 404

    update_fields = []
    params = {}
    
    if 'password' in data:
        update_fields.append("password = :password")
        params['password'] = data['password']
    if 'email' in data:
        valid_email = r"^.+\d*@.+[.][a-zA-Z]{2,4}$"
        if(re.search(valid_email, data['email']) == None):
            return ResponseMessage("Invalid email.", 400)
        update_fields.append("email = :email")
        params['email'] = data['email']
    if 'first_name' in data:
        update_fields.append("first_name = :first_name")
        params['first_name'] = data['first_name']
    if 'last_name' in data:
        update_fields.append("last_name = :last_name")
        params['last_name'] = data['last_name']
    if 'phone_number' in data:
        data['phone_number'] = re.sub(r"(-|\s|\)|\()", "", str(data['phone_number']))
        valid_phone = r"^\d{10}$"
        if(re.search(valid_phone, str(data['phone_number'])) == None):
            return ResponseMessage("Invalid phone number.", 400)
        update_fields.append("phone_number = :phone_number")
        params['phone_number'] = data['phone_number']

    if not update_fields:
        return {"error": "No update fields provided."}, 400
    
    params['user_id'] = user_id
    query = "UPDATE users SET " + ", ".join(update_fields) + " WHERE user_id = :user_id"
    
    try:
        db.session.execute(text(query), params)
        db.session.commit()
    except Exception as e:
        print(e)
        return {"error": "Error updating user"}, 500

    return {"message": "user updated successfully"}, 200

@app.route("/users/<string:role>", methods=['POST'])
@swag_from('docs/users/post.yml')
def create_user(role):
    file = request.files.get('identification')
    identification_path = ""
    user_id = (db.session.execute(text("SELECT MAX(user_id) + 1 AS user_id FROM users")).first()).user_id
    if file and allowed_file(file.filename):
        ext = os.path.splitext(file.filename)[1].lower()
        new_filename = f"{user_id}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)
        identification_path = filepath
    #sql query
    user_query = text("""
        INSERT INTO users (user_id, email, password, first_name, last_name, phone_number, role, created_at, identification)
        VALUES (
            :user_id,
            :email,
            :password,
            :first_name,
            :last_name,
            :phone_number,
            :role,
            CURRENT_TIMESTAMP,
            :identification)
    """)
    patient_query = text("""
        INSERT INTO patients (patient_id, address_id, medical_history, creditcard_id, ssn)
        VALUES (
            :patient_id,
            :address_id,
            :medical_history,
            :creditcard_id,
            :ssn
        )
    """)
    pharmacist_query = text("""
        INSERT INTO pharmacists (pharmacist_id, pharmacy_location)
        VALUES (:pharmacist_id, :pharmacy_location)
    """)
    doctor_query = text("""
        INSERT INTO doctors (doctor_id, license_number, specialization, profile)
        VALUES (
            :doctor_id,
            :license_number,
            :specialization,
            :profile
        )
    """)
    creditcard_query = text("""
        INSERT INTO credit_card (creditcard_id, cardnumber, cvv, exp_date)
        VALUES (
            :creditcard_id,
            :cardnumber,
            :cvv,
            :exp_date
        )
    """)
    address_query = text("""
        INSERT INTO address (address_id, city, country, address2, address, zip, state)
        VALUES (
            :address_id,
            :city, 
            :country,
            :address2,
            :address,
            :zip,
            :state
        )
    """)
    # NOTE: doing appointment_id this way could bring about a race condition.... but lets be real this is never happening.
    try:
        user_json = json.loads(request.form.get('user'))
        doctor_json = json.loads(request.form.get('doctor')) if request.form.get('doctor') else None
        patient_json = json.loads(request.form.get('patient')) if request.form.get('patient') else None
        pharmacist_json = json.loads(request.form.get('pharmacist')) if request.form.get('pharmacist') else None
        address_json = json.loads(request.form.get("address")) if request.form.get('address') else None
        creditcard_json = json.loads(request.form.get("credit_card")) if request.form.get('credit_card') else None
    except Exception as e:
        return ResponseMessage(f"Malformed JSON: {e}", 400)
    
    user_params = {
        'user_id': user_id,
        'email': user_json.get('email'),
        'password': user_json.get('password'),
        'first_name': user_json.get('first_name'),
        'last_name': user_json.get('last_name'),
        'phone_number': user_json.get('phone_number'),
        'role': role,
        'identification': identification_path
    }
    doctor_params = {
        'doctor_id': user_params['user_id'],
        'license_number': doctor_json.get('license_number'),
        'specialization': doctor_json.get('specialization'),
        'profile': doctor_json.get('profile') if doctor_json.get('profile') != "" else "N/A",
    } if doctor_json != None else None 
    pharmacist_params = {
        'pharmacist_id': user_params['user_id'],
        'pharmacy_location': pharmacist_json.get('pharmacy_location'),
    } if pharmacist_json != None else None 
    address_params = {
        'address_id': (db.session.execute(text("SELECT MAX(address_id) + 1 AS address_id FROM address")).first()).address_id,
        'address2': address_json.get('address2'),
        'state': address_json.get('state'),
        'city': address_json.get('city'),
        'country': address_json.get('country'),
        'address': address_json.get('address'),
        'zip': address_json.get('zip'),
    } if address_json != None else None 
    creditcard_params = {
        'creditcard_id': (db.session.execute(text("SELECT MAX(creditcard_id) + 1 AS creditcard_id FROM credit_card")).first()).creditcard_id,
        'cardnumber': creditcard_json.get('cardnumber'),
        'cvv': creditcard_json.get('cvv'),
        'exp_date': creditcard_json.get('exp_date'),
    } if creditcard_json != None else None 
    patient_params = {
        'patient_id': user_params['user_id'],
        'address_id': address_params['address_id'],
        'medical_history': patient_json.get('medical_history'),
        'creditcard_id': creditcard_params['creditcard_id'],
        'ssn': patient_json.get('ssn')
    } if patient_json != None else None 
    #input validation
    valid_email = r"^.+\d*@.+[.][a-zA-Z]{2,4}$" # tried looking up a real email regex and its a nightmare. this will suffice. hopefully.
    valid_phone = r"^\d{10}$"
    valid_license = r"^\d{9}$"
    valid_address = r"\d{1,5}(\s\w.)?\s(\b\w*\b\s){1,2}\w*\.?" #dangerous regex
    valid_zip = r"^\d{1,5}$"
    valid_cardnum = r"^\d{14,18}$"
    valid_cvv = r"^\d{3}$"
    valid_date = r"\d{4}-\d{2}-\d{2}"
    if None in list(user_params.values())[1:]:
        return ResponseMessage("Required parameters missing from user fields.", 400)
    user_params['phone_number'] = re.sub(r"(-|\s|\)|\()", "", user_params['phone_number'])
    user_params['role'] = user_params['role'].lower()
    if(re.search(valid_email, user_params['email']) == None):
        return ResponseMessage("Invalid email.", 400)
    if(len(user_params['password']) < 4):
        return ResponseMessage("Password must be at least 4 characters.", 400)
    if(len(user_params['first_name']) < 1 or len(user_params['last_name']) < 1):
        return ResponseMessage("Name fields must be non-empty.", 400)
    if(re.search(valid_phone, str(user_params['phone_number'])) == None):
        return ResponseMessage("Invalid phone number.", 400)
    if(user_params['role'] not in ('doctor', 'patient', 'pharmacist')):
        return ResponseMessage("Invalid user role. (must be 'doctor', 'patient', or 'pharmacist')", 400)
    #input validation based on role
    if(user_params['role'] == 'doctor'):
        if(re.search(valid_license, str(doctor_params['license_number'])) == None):
            return ResponseMessage("Invalid license number, must be 9 digits", 400)
        if(len(doctor_params['specialization']) == 0):
            return ResponseMessage("Specialization must be nonempty", 400)
    elif(user_params['role'] == 'patient'):
        #user fields
        if(None in patient_params.values()):
            return ResponseMessage("Required parameters missing from patient fields.", 400)
        
        if(patient_params['medical_history'] == ""):
            return ResponseMessage("Unless newborn babies are beginning their weight loss journey young, medical history should be non-empty", 400)
        if(re.search(valid_license, str(patient_params['ssn'])) == None):
            return ResponseMessage("Invalid SSN.", 400)
        #address fields
        if(None in list(address_params.values())[3:]):
            return ResponseMessage("Required parameters missing from address fields.", 400)
        address_params['address2'] = "" if address_params['address2'] == None else address_params['address2']
        address_params['state'] = "" if address_params['state'] == None else address_params['state'].upper()
        if(re.search(valid_address, address_params['address']) == None):
            return ResponseMessage("Invalid street address format.", 400)
        if(len(address_params['city']) == 0):
            return ResponseMessage("City must be non-empty", 400)
        if(len(address_params['country']) == 0):
            return ResponseMessage("Country must be non-empty", 400)
        if(re.search(valid_zip, str(address_params['zip'])) == None or address_params['zip'] == 0):
            return ResponseMessage("Invalid zip code format.", 400)
        #credit card fields
        if(None in list(creditcard_params.values())[1:]):
            return ResponseMessage("Required parameters missing from credit card fields.", 400)
        if(re.search(valid_date, creditcard_params['exp_date']) == None):
            return ResponseMessage("Invalid expiration date.", 400)
        if(re.search(valid_cardnum, str(creditcard_params['cardnumber'])) == None):
            return ResponseMessage("Invalid creditcard number.", 400)
        if(re.search(valid_cvv, str(creditcard_params['cvv'])) == None):
            return ResponseMessage("Invalid credit card CVV.", 400)
    elif(user_params['role'] == 'pharmacist'):
        if None in pharmacist_params.values():
            return ResponseMessage("Required parameters missing from pharmacist fields.", 400)
        if(re.search(valid_address, pharmacist_params['pharmacy_location']) == None):
            return ResponseMessage("Invalid address.", 400)
    #execute query
    try:
        db.session.execute(user_query, user_params)
        if(user_params['role'] == 'pharmacist'):
            db.session.execute(pharmacist_query, pharmacist_params)
        elif(user_params['role'] == 'doctor'):
            db.session.execute(doctor_query, doctor_params)
        elif(user_params['role'] == 'patient'):
            db.session.execute(address_query, address_params)
            db.session.execute(creditcard_query, creditcard_params)
            db.session.execute(patient_query, patient_params)
    except Exception as e:
        print(e)
        return ResponseMessage(f"Server/SQL Error. Exception: \n{e}", 500)
    else:
        db.session.commit()
        return ResponseMessage(f"User succesfully created. (id: {user_params['user_id']})", 201)
        
def ResponseMessage(message, code):
    return {'message': message}, code

if __name__ == "__main__":
    app.run(debug=True)
