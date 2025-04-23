import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import text
from app import app, db

@pytest.fixture
def client():

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SECRET_KEY='test-secret'
    )
    with app.app_context():

        for tbl, ddl in {
            'patients': "CREATE TABLE patients (patient_id INTEGER PRIMARY KEY)",
            'doctors': "CREATE TABLE doctors (doctor_id INTEGER PRIMARY KEY)",
            'pharmacists': "CREATE TABLE pharmacists (pharmacist_id INTEGER PRIMARY KEY)",
            'medications': "CREATE TABLE medications (medication_id INTEGER PRIMARY KEY)"
        }.items():
            db.session.execute(text(f"DROP TABLE IF EXISTS {tbl}"))
            db.session.execute(text(ddl))

        db.session.execute(text("INSERT INTO patients (patient_id) VALUES (201)"))
        db.session.execute(text("INSERT INTO doctors (doctor_id) VALUES (101)"))
        db.session.execute(text("INSERT INTO pharmacists (pharmacist_id) VALUES (401)"))
        db.session.execute(text("INSERT INTO medications (medication_id) VALUES (301)"))

        db.session.execute(text("DROP TABLE IF EXISTS prescriptions"))
        db.session.execute(text("""
            CREATE TABLE prescriptions (
                prescription_id INTEGER PRIMARY KEY,
                doctor_id INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                medication_id INTEGER NOT NULL,
                pharmacist_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                date_prescribed TEXT NOT NULL,
                instructions TEXT,
                quantity INTEGER NOT NULL
            )
        """))

        db.session.execute(text("""
            INSERT INTO prescriptions
              (prescription_id, doctor_id, patient_id, medication_id, pharmacist_id, status, date_prescribed, instructions, quantity)
            VALUES
              (1, 101, 201, 301, 401, 'pending',   '2025-04-20', 'Take daily', 30),
              (2, 102, 202, 302, 402, 'completed', '2025-04-21', 'Take with food', 60)
        """))
        db.session.commit()
    with app.test_client() as c:
        yield c

# GET /prescriptions

def test_get_all_prescriptions(client):
    resp = client.get('/prescriptions')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'prescriptions' in data
    assert len(data['prescriptions']) == 2


def test_filter_by_prescription_id(client):
    resp = client.get('/prescriptions?prescription_id=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['prescriptions']) == 1
    assert data['prescriptions'][0]['prescription_id'] == 1


def test_filter_by_status(client):
    resp = client.get('/prescriptions?status=pend')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['prescriptions']) == 1
    assert data['prescriptions'][0]['status'] == 'pending'


def test_filter_by_date_prescribed(client):
    resp = client.get('/prescriptions?date_prescribed=2025-04-21')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['prescriptions']) == 1
    assert data['prescriptions'][0]['date_prescribed'] == '2025-04-21'

# DELETE /prescriptions/<id>

def test_delete_nonexistent_prescription(client):
    resp = client.delete('/prescriptions/999')
    assert resp.status_code == 400


def test_delete_existing_prescription(client):
    resp = client.delete('/prescriptions/1')
    assert resp.status_code == 200
    resp2 = client.delete('/prescriptions/1')
    assert resp2.status_code == 400

# PATCH /prescriptions/<id>

def test_patch_no_params_returns_200(client):
    resp = client.patch('/prescriptions/2', json={})
    assert resp.status_code == 200
    assert b"No parameters were passed to update" in resp.data

@pytest.mark.parametrize('payload,code,msg', [
    ({'quantity': 0}, 400, b"Quantity must be >0"),
    ({'status': 'invalid', 'quantity': 1}, 400, b"Invalid status field"),
    ({'date_prescribed': 'bad-date', 'quantity': 1}, 400, b"Invalid Start Time"),
])
def test_patch_validation_errors(client, payload, code, msg):
    resp = client.patch('/prescriptions/2', json=payload)
    assert resp.status_code == code
    assert msg in resp.data

# POST /prescriptions

def test_post_missing_parameters(client):
    resp = client.post('/prescriptions', json={'doctor_id': 101, 'medication_id': 301, 'pharmacist_id': 401, 'quantity': 10, 'instructions': 'ok'})
    assert resp.status_code == 400
    assert b"Required parameters not supplied" in resp.data


def test_post_successful_insertion(client, monkeypatch):

    monkeypatch.setattr('app.order_prescription', lambda *args, **kwargs: None)
    payload = {
        'doctor_id': 101,
        'patient_id': 201,
        'medication_id': 301,
        'pharmacist_id': 401,
        'quantity': 15,
        'instructions': 'Take twice'
    }
    resp = client.post('/prescriptions', json=payload)
    assert resp.status_code == 201
    assert b"Prescription entry successfully created" in resp.data

    get_resp = client.get('/prescriptions?prescription_id=3')
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert len(data['prescriptions']) == 1
    entry = data['prescriptions'][0]
    assert entry['prescription_id'] == 3
    assert entry['quantity'] == 15
