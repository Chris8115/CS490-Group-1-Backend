import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import text
from datetime import datetime, timedelta
from app import app, db

@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SECRET_KEY='test-secret',
        LOGIN_DISABLED=True
    )
    with app.app_context():
        # Create dependency tables
        for tbl, ddl in {
            'patients': "CREATE TABLE patients (patient_id INTEGER PRIMARY KEY)",
            'appointments': ""
        }.items():
            if tbl != 'appointments':
                db.session.execute(text(f"DROP TABLE IF EXISTS {tbl}"))
                db.session.execute(text(ddl))
        # Drop and recreate appointments
        db.session.execute(text("DROP TABLE IF EXISTS appointments"))
        db.session.execute(text("""
            CREATE TABLE appointments (
                appointment_id INTEGER PRIMARY KEY,
                doctor_id      INTEGER NOT NULL,
                patient_id     INTEGER NOT NULL,
                start_time     TEXT    NOT NULL,
                end_time       TEXT    NOT NULL,
                status         TEXT    NOT NULL,
                location       TEXT,
                reason         TEXT,
                details        TEXT,
                created_at     TEXT    NOT NULL,
                notes          TEXT
            )
        """))
        db.session.execute(text("DROP TABLE IF EXISTS doctors"))
        db.session.execute(text("""
            CREATE TABLE "doctors" (
            "doctor_id"	INTEGER NOT NULL,
            "rate"	REAL NOT NULL DEFAULT 59.99,
            PRIMARY KEY("doctor_id"),
        )
        """))
        db.session.execute(text("DROP TABLE IF EXISTS transactions"))
        db.session.execute(text("""
            CREATE TABLE "transactions" (
            "transaction_id"	INTEGER NOT NULL,
            "patient_id"	INTEGER,
            "doctor_id"	INTEGER,
            "service_fee"	REAL NOT NULL,
            "doctor_fee"	REAL NOT NULL,
            "subtotal"	REAL NOT NULL,
            "created_at"	TIMESTAMP NOT NULL,
            "creditcard_id"	INTEGER,
            CONSTRAINT "transactions_pk" PRIMARY KEY("transaction_id"),
            CONSTRAINT "creditcard_id" FOREIGN KEY("creditcard_id") REFERENCES "credit_card"("creditcard_id"),
            CONSTRAINT "doctor_id" FOREIGN KEY("doctor_id") REFERENCES "doctors"("doctor_id"),
            CONSTRAINT "customer_id" FOREIGN KEY("patient_id") REFERENCES "patients"("patient_id")
        )                  
        """))
        # Seed dependency rows
        db.session.execute(text("INSERT INTO patients (patient_id) VALUES (201)"))
        db.session.execute(text("INSERT INTO doctors  (doctor_id)   VALUES (101)"))
        # Seed appointments
        now = datetime(2025,4,23,10,0,0).strftime("%Y-%m-%d %H:%M:%S")
        later = (datetime(2025,4,23,10,0,0) + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        db.session.execute(text(
            "INSERT INTO appointments (appointment_id, doctor_id, patient_id, start_time, end_time, status, location, reason, details, created_at, notes) VALUES (1,101,201,:st,:et,'pending','Office','Checkup','Det','2025-04-23 09:00:00','Note')"
        ), {'st': now, 'et': later})
        db.session.commit()
    with app.test_client() as c:
        yield c

# GET

def test_get_appointments(client):
    rv = client.get('/appointments')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data['appointments']) == 1

# DELETE

def test_delete_nonexistent(client):
    rv = client.delete('/appointments/999')
    assert rv.status_code == 400

def test_delete_existing(client):
    rv = client.delete('/appointments/1')
    assert rv.status_code == 200
    # now none
    rv2 = client.get('/appointments')
    assert len(rv2.get_json()['appointments']) == 0

# POST

def test_post_missing_params(client):
    payload = {'doctor_id':101,'patient_id':201,'start_time':'2025-04-24 10:00:00','status':'pending'}
    rv = client.post('/appointments', json=payload)
    assert rv.status_code == 400
    assert b'Required parameters not supplied' in rv.data

def test_post_success(client):
    payload = {
        'doctor_id':101,'patient_id':201,'start_time':'2025-04-24 10:00:00',
        'status':'pending','reason':'Visit'
    }
    rv = client.post('/appointments', json=payload)
    assert rv.status_code == 201
    assert b'Appointment entry successfully created' in rv.data

# PATCH

def test_patch_not_found(client):
    rv = client.patch('/appointments/999', json={'status':'canceled'})
    assert rv.status_code == 404

def test_patch_no_fields(client):
    rv = client.patch('/appointments/1', json={})
    assert rv.status_code == 200
    # Endpoint treats empty fields as a successful no-op update
    assert b"Appointment Successfully Updated" in rv.data


def test_patch_invalid_status(client):
    rv = client.patch('/appointments/1', json={'status':'bad'})
    assert rv.status_code == 400
    assert b'Invalid status field' in rv.data

def test_patch_success(client):
    rv = client.patch('/appointments/1', json={'status':'accepted','reason':'Follow-up'})
    assert rv.status_code == 200
    # verify change
    rv2 = client.get('/appointments')
    appt = rv2.get_json()['appointments'][0]
    assert appt['status']=='accepted'
    assert appt['reason']=='Follow-up'

def test_get_filter_by_appointment_and_patient(client):
    rv = client.get('/appointments?appointment_id=1&patient_id=201')
    data = rv.get_json()['appointments']
    assert len(data) == 1 and data[0]['appointment_id']==1

def test_post_invalid_datetime_format(client):
    payload = {
        'doctor_id':101,'patient_id':201,
        'start_time':'2025-99-99 99:99:99',
        'status':'pending','reason':'Visit'
    }
    rv = client.post('/appointments', json=payload)
    assert rv.status_code == 400
    assert b'Invalid Start Time' in rv.data

def test_post_invalid_status(client):
    payload = {
        'doctor_id':101,'patient_id':201,'start_time':'2025-04-24 10:00:00',
        'status':'foo','reason':'Visit'
    }
    rv = client.post('/appointments', json=payload)
    assert rv.status_code == 400
    assert b'Invalid status field' in rv.data

def test_post_empty_reason(client):
    payload = {
        'doctor_id':101,'patient_id':201,'start_time':'2025-04-24 10:00:00',
        'status':'pending','reason':''
    }
    rv = client.post('/appointments', json=payload)
    assert rv.status_code == 400
    assert b'Reason must be non-empty' in rv.data

def test_post_conflicting_timeslot(client):
    # existing is 10:00–11:00 on 2025-04-23
    payload = {
        'doctor_id':101,'patient_id':201,'start_time':'2025-04-23 10:30:00',
        'status':'pending','reason':'Overlap'
    }
    rv = client.post('/appointments', json=payload)
    assert rv.status_code == 400
    assert b'Invalid timeslot' in rv.data

def test_patch_invalid_datetime_format(client):
    rv = client.patch('/appointments/1', json={'start_time':'bad-date'})
    assert rv.status_code == 400
    assert b'Invalid Start Time' in rv.data

def test_patch_empty_reason(client):
    rv = client.patch('/appointments/1', json={'reason':''})
    assert rv.status_code == 400
    assert b'Reason must be non-empty' in rv.data

def test_patch_conflicting_timeslot(client):
    # seed a second appointment for the same doctor at 12:00–13:00
    now = '2025-04-23 12:00:00'; later = '2025-04-23 13:00:00'
    with app.app_context():
        db.session.execute(text(
            "INSERT INTO appointments (appointment_id,doctor_id,patient_id,start_time,end_time,status,created_at) "
            "VALUES (3,101,201,:st,:et,'pending',CURRENT_TIMESTAMP)"
        ), {'st': now, 'et': later})
        db.session.commit()
    # now try to move appt #1 into that slot
    rv = client.patch('/appointments/1', json={'start_time':'2025-04-23 12:30:00'})
    assert rv.status_code == 400
    assert b'Invalid timeslot' in rv.data
