import os
import sys
from datetime import datetime, timezone
import pytest
from sqlalchemy import text
from flask import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app, db

@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        LOGIN_DISABLED=True
    )
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS doctor_patient_relationship"))
        db.session.execute(text("""
            CREATE TABLE doctor_patient_relationship (
                doctor_id INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                date_assigned TEXT NOT NULL,
                notes TEXT,
                PRIMARY KEY (doctor_id, patient_id)
            )
        """))
        db.session.execute(text("""
            INSERT INTO doctor_patient_relationship (doctor_id, patient_id, status, date_assigned, notes)
            VALUES (1, 100, 'active', :dt, 'Initial entry')
        """), {'dt': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")})
        db.session.commit()
    with app.test_client() as c:
        yield c


def test_get_all_relationships(client):
    res = client.get("/doctor_patient_relationship")
    assert res.status_code == 200
    assert len(res.get_json()['doctor_patient_relationship']) == 1

def test_get_filtered_relationship(client):
    res = client.get("/doctor_patient_relationship?doctor_id=1")
    assert res.status_code == 200
    assert res.get_json()['doctor_patient_relationship'][0]['doctor_id'] == 1

def test_post_missing_fields(client):
    res = client.post("/doctor_patient_relationship", json={"doctor_id": 1})
    assert res.status_code == 400
    assert b"Missing required fields" in res.data

def test_post_empty_status(client):
    res = client.post("/doctor_patient_relationship", json={"doctor_id": 2, "patient_id": 200, "status": ""})
    assert res.status_code == 400
    assert b"Status cannot be empty" in res.data

def test_post_success(client):
    res = client.post("/doctor_patient_relationship", json={"doctor_id": 2, "patient_id": 200, "status": "active"})
    assert res.status_code == 201
    assert b"created successfully" in res.data

def test_patch_not_found(client):
    res = client.patch("/doctor_patient_relationship/999/999", json={"status": "inactive"})
    assert res.status_code == 404

def test_patch_empty_status(client):
    res = client.patch("/doctor_patient_relationship/1/100", json={"status": ""})
    assert res.status_code == 400
    assert b"Status cannot be empty" in res.data

def test_patch_success(client):
    res = client.patch("/doctor_patient_relationship/1/100", json={"status": "inactive"})
    assert res.status_code == 200
    assert b"updated successfully" in res.data

def test_delete_nonexistent(client):
    res = client.delete("/doctor_patient_relationship/9/9")
    assert res.status_code == 400

def test_delete_success(client):
    res = client.delete("/doctor_patient_relationship/1/100")
    assert res.status_code == 200
