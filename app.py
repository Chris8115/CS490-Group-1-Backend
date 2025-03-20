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

@app.route("/forum_posts", methods=['GET'])
def forum_posts():
    #sql query
    query = "SELECT * FROM forum_posts\n"
    #get inputs
    params = {
        'pid': "" if request.args.get('post_id') == None else request.args.get('post_id'),
        'uid': "" if request.args.get('user_id') == None else request.args.get('user_id'),
        'title': "" if request.args.get('title') == None else '%' + request.args.get('title') + '%',
        'type': "" if request.args.get('post_type') == None else '%' + request.args.get('post_type') + '%',
    }
    if(params['pid'] != "" or params['uid'] != "" or params['title'] != "" or params['type'] != ""):
        query += ("WHERE " + ("post_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("user_id = :uid\n" if params['uid'] != "" else "TRUE\n"))
        query += ("AND " + ("title LIKE :title\n" if params['title'] != "" else "TRUE\n"))
        query += ("AND " + ("post_type LIKE :type\n" if params['type'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
    json = {'forum_posts': []}
    for row in result:
        json['forum_posts'].append({
            'post_id': row.post_id,
            'user_id': row.user_id,
            'title': row.title,
            'content': row.content,
            'post_type': row.post_type,
            'created_at': row.created_at
        })
    return json, 200

@app.route("/appointments", methods=['GET'])
def appointments():
    #sql query
    query = "SELECT * FROM appointments\n"
    #get inputs
    params = {
        'aid': "" if request.args.get('appointment_id') == None else request.args.get('appointment_id'),
        'did': "" if request.args.get('doctor_id') == None else request.args.get('doctor_id'),
        'pid': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'status': "" if request.args.get('status') == None else '%' + request.args.get('status') + '%',
        'reason': "" if request.args.get('reason') == None else '%' + request.args.get('reason') + '%'
    }
    if(params['aid'] != "" or params['did'] != "" or params['pid'] != "" or params['status'] != "" or params['reason'] != ""):
        query += ("WHERE " + ("appointment_id = :aid\n" if params['aid'] != "" else "TRUE\n"))
        query += ("AND " + ("doctor_id = :did\n" if params['did'] != "" else "TRUE\n"))
        query += ("AND " + ("patient_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
        query += ("AND " + ("status LIKE :status\n" if params['status'] != "" else "TRUE\n"))
        query += ("AND " + ("reason LIKE :reason\n" if params['reason'] != "" else "TRUE\n"))
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
            'created_at': row.created_at
        })
    return json, 200

@app.route("/patients", methods=['GET'])
def patients():
    #sql query
    query = "SELECT * FROM patients\n"
    #get inputs
    params = {
        'id': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
    }
    if(params['id'] != ""):
        query += ("WHERE " + ("patient_id = :id\n" if params['id'] != "" else "TRUE\n"))
    #execute query
    result = db.session.execute(text(query), params)
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

@app.route("/users", methods=['GET'])
def users():
    #sql query
    query = "SELECT * FROM users\n"
    #get inputs
    params = {
        'id': "" if request.args.get('user_id') == None else request.args.get('user_id'),
        'role': "" if request.args.get('role') == None else request.args.get('role'),
        'fname': "" if request.args.get('first_name') == None else '%' + request.args.get('first_name') + '%',
        'lname': "" if request.args.get('last_name') == None else '%' + request.args.get('last_name') + '%',
    }
    if(params['id'] != "" or params['role'] != "" or params['fname'] != "" or params['lname'] != ""):
        query += ("WHERE " + ("user_id = :id\n" if params['id'] != "" else "TRUE\n"))
        query += ("AND " + ("role = :role\n" if params['role'] != "" else "TRUE\n"))
        query += ("AND " + ("first_name LIKE :fname\n" if params['fname'] != "" else "TRUE\n"))
        query += ("AND " + ("last_name LIKE :lname\n" if params['lname'] != "" else "TRUE\n"))
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

@app.route("/reviews", methods=['GET'])
def reviews():
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


if __name__ == "__main__":
    app.run(debug=True)