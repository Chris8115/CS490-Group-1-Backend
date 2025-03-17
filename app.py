from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from sqlalchemy import desc, text
from sqlalchemy.dialects import mysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///craze.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route("/")
def home():
    return "<h1>It works!</h1>"

@app.route("/patients", methods=['GET'])
def patients():
    #sql query
    query = "SELECT * FROM patients"
    filter = "\nWHERE patient_id = :id"
    #get inputs
    patient_id = "" if request.args.get('patient_id') == None else request.args.get('patient_id')
    query += filter if(patient_id != "") else ""
    #execute query
    result = db.session.execute(text(query), {
        'id': patient_id,
    })
    json = {'patients': []}
    for row in result:
        json['patients'].append({
            'patient_id': row.patient_id,
            'address_id': row.address_id,
            'medical_history': row.medical_history,
            'creditcard_id': row.creditcard_id
        })
    return json, 200

@app.route("/doctors", methods=['GET'])
def doctors():
    #sql query
    query = "SELECT * FROM doctors"
    filter = """\n
        WHERE
            doctor_id = :id
            OR license_number = :license
            OR specialization LIKE :special
    """
    #get inputs
    doctor_id = "" if request.args.get('doctor_id') == None else request.args.get('doctor_id')
    license_number = "" if request.args.get('license_number') == None else request.args.get('license_number')
    specialization = "" if request.args.get('specialization') == None else '%' + request.args.get('specialization') + '%'
    query += filter if(doctor_id != "" or license_number != "" or specialization != "") else ""
    #execute query
    result = db.session.execute(text(query), {
        'id': doctor_id,
        'license': license_number,
        'special': specialization,
    })
    json = {'doctors': []}
    for row in result:
        json['doctors'].append({
            'doctor_id': row.doctor_id,
            'license_number': row.license_number,
            'specialization': row.specialization,
            'profile': row.profile
        })
    return json, 200

@app.route("/users", methods=['GET'])
def users():
    #sql query
    query = "SELECT * FROM users"
    filter = """\n
        WHERE
            user_id = :id
            OR role = :role
            OR first_name LIKE :fname
            OR last_name LIKE :lname
    """
    #get inputs
    user_id = "" if request.args.get('user_id') == None else request.args.get('user_id')
    role = "" if request.args.get('role') == None else request.args.get('role')
    first_name = "" if request.args.get('first_name') == None else '%' + request.args.get('first_name') + '%'
    last_name = "" if request.args.get('last_name') == None else '%' + request.args.get('last_name') + '%'
    query += filter if(user_id != "" or role != "" or first_name != "" or last_name != "") else ""
    #execute query
    result = db.session.execute(text(query), {
        'id': user_id,
        'role': role,
        'fname': first_name,
        'lname': last_name,
    })
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

if __name__ == "__main__":
    app.run(debug=True)