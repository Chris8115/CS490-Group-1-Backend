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

@app.route("/exercise_plans", methods=['GET'])
def exercise_plans():
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

@app.route("/doctor_patient_relationship", methods=['GET'])
def doctor_patient_relationship():
    #sql query
    query = "SELECT * FROM doctor_patient_relationship\n"
    #get inputs
    params = {
        'did': "" if request.args.get('doctor_id') == None else request.args.get('doctor_id'),
        'pid': "" if request.args.get('patient_id') == None else request.args.get('patient_id'),
        'status': "" if request.args.get('status') == None else '%' + request.args.get('status') + '%',
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

@app.route("/credit_card", methods=['GET'])
def credit_card():
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

@app.route("/address", methods=['GET'])
def address():
    #sql query
    query = "SELECT * FROM address\n"
    #get inputs
    params = {
        'aid': "" if request.args.get('address_id') == None else request.args.get('address_id'),
        'zip': "" if request.args.get('zip') == None else request.args.get('zip'),
        'city': "" if request.args.get('city') == None else '%' + request.args.get('city') + '%',
        'addr': "" if request.args.get('address') == None else '%' + request.args.get('address') + '%',
        'addr2': "" if request.args.get('address2') == None else '%' + request.args.get('address2') + '%',
    }
    if(params['aid'] != "" or params['zip'] != "" or params['city'] != "" or params['addr'] != "" or params['addr2'] != ""):
        query += ("WHERE " + ("address_id = :aid\n" if params['aid'] != "" else "TRUE\n"))
        query += ("AND " + ("zip = :zip\n" if params['zip'] != "" else "TRUE\n"))
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
            'address2': row.address2,
            'address': row.address,
            'zip': row.zip
        })
    return json, 200

@app.route("/pharmacists", methods=['GET'])
def pharmacists():
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

@app.route("/forum_comments", methods=['GET'])
def forum_comments():
    #sql query
    query = "SELECT * FROM forum_comments\n"
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
            'comment_text': row.comment_text,
            'created_at': row.created_at
        })
    return json, 200

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