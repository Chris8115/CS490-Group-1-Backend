from flask import Flask, request, Response, jsonify ,render_template
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import func
from sqlalchemy import desc, text
from sqlalchemy.dialects import mysql
from flasgger import Swagger, swag_from

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///craze.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER'] = {
    'title': 'BetterU API',
    'description': 'The available endpoints for the BetterU service.',
    'termsOfService': None,
    'doc_dir': './docs/',
    'uiversion': 3,
}
db = SQLAlchemy(app)
#API docs stuff
api = Api(app)
swag = Swagger(app)

@app.route("/")
def home():
    return "<h1>It works!</h1>"

@app.route("/docs")
def docs():
    return render_template("build/html/index.html")

class Transactions(Resource):
    def get(self):
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

class SavedPosts(Resource):
    def get(self):
        #sql query
        query = "SELECT * FROM saved_posts\n"
        #get inputs
        params = {
            'uid': "" if request.args.get('user_id') == None else request.args.get('user_id'),
            'pid': "" if request.args.get('post_id') == None else request.args.get('post_id'),
            'datetime': "" if request.args.get('saved_at') == None else '%' + request.args.get('saved_at') + '%'
        }
        if(params['uid'] != "" or params['pid'] != "" or params['datetime'] != ""):
            query += ("WHERE " + ("user_id = :uid\n" if params['uid'] != "" else "TRUE\n"))
            query += ("AND " + ("post_id = :pid\n" if params['pid'] != "" else "TRUE\n"))
            query += ("AND " + ("saved_at LIKE :datetime\n" if params['datetime'] != "" else "TRUE\n"))
        #execute query
        result = db.session.execute(text(query), params)
        json = {'saved_posts': []}
        for row in result:
            json['saved_posts'].append({
                'user_id': row.user_id,
                'post_id': row.post_id,
                'saved_at': row.saved_at
            })
        return json, 200

class Prescriptions(Resource):
    def get(self):
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

class PatientProgress(Resource):
    def get(self):
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
        #execute query
        result = db.session.execute(text(query), params)
        json = {'patient_progress': []}
        for row in result:
            json['patient_progress'].append({
                'progress_id': row.progress_id,
                'patient_id': row.patient_id,
                'weight': row.weight,
                'calories': row.calories,
                'notes': row.notes,
                'date_logged': row.date_logged
            })
        return json, 200

class PatientExerciseAssignments(Resource):
    def get(self):
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
                'instructions': row.instructions,
                'assigned_at': row.assigned_at
            })
        return json, 200

class Medications(Resource):
    def get(self):
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

class Inventory(Resource):
    def get(self):
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

class ExercisePlans(Resource):
    def get(self):
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

class DoctorPatientRelationship(Resource):
    def get(self):
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

class CreditCard(Resource):
    def get(self):
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

class Address(Resource):
    def get(self):
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

class Pharmacists(Resource):
    def get(self):
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

class ForumComments(Resource):
    def get(self):
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

class ForumPosts(Resource):
    def get(self):
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

class Appointments(Resource):
    def get(self):
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

class Patients(Resource):
    def get(self):
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

class Doctors(Resource):
    def get(self):
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

class Users(Resource):
    def get(self):
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

class Reviews(Resource):
    def get(self):
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

api.add_resource(Transactions,'/transactions')
api.add_resource(SavedPosts,'/saved_posts')
api.add_resource(Prescriptions,'/prescriptions')
api.add_resource(PatientProgress,'/patient_progress')
api.add_resource(PatientExerciseAssignments,'/patient_exercise_assignments')
api.add_resource(Medications,'/medications')
api.add_resource(Inventory,'/inventory')
api.add_resource(ExercisePlans,'/exercise_plans')
api.add_resource(DoctorPatientRelationship,'/doctor_patient_relationship')
api.add_resource(CreditCard,'/credit_card')
api.add_resource(Address,'/address')
api.add_resource(Pharmacists,'/pharmacists')
api.add_resource(ForumComments,'/forum_comments')
api.add_resource(ForumPosts,'/forum_posts')
api.add_resource(Appointments,'/appointments')
api.add_resource(Patients,'/patients')
api.add_resource(Doctors,'/doctors')
api.add_resource(Users,'/users')
api.add_resource(Reviews,'/reviews')

if __name__ == "__main__":
    app.run(debug=True)