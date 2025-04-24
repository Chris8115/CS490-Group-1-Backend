import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask import Response
from datetime import datetime, timedelta
from sqlalchemy import text

from app import app, db

@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret",
        LOGIN_DISABLED=True
    )
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS patient_exercise_assignments"))
        db.session.execute(text("""
            CREATE TABLE patient_exercise_assignments (
                assignment_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id          INTEGER NOT NULL,
                doctor_id           INTEGER NOT NULL,
                exercise_id         INTEGER NOT NULL,
                frequency_per_week  INTEGER,
                reps                INTEGER,
                sets                INTEGER,
                assigned_at         TEXT  NOT NULL
            )
        """))
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        older = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        for idx, ts in enumerate((now, older), start=1):
            db.session.execute(text("""
                INSERT INTO patient_exercise_assignments
                  (patient_id, doctor_id, exercise_id, frequency_per_week, reps, sets, assigned_at)
                VALUES (:pid, :did, :eid, :freq, :reps, :sets, :ts)
            """), {
                "pid": 10 + idx,
                "did": 20 + idx,
                "eid": 30 + idx,
                "freq": 3 * idx,
                "reps": 10 * idx,
                "sets": 2 * idx,
                "ts": ts
            })
        db.session.commit()
    with app.test_client() as c:
        yield c

def test_get_all_assignments(client):
    rv = client.get("/patient_exercise_assignments")
    assert rv.status_code == 200
    arr = rv.get_json()["patient_exercise_assignments"]
    assert len(arr) == 2
    assert arr[0]["frequency_per_week"] == 3

def test_get_filter_by_assignment_id(client):
    rv = client.get("/patient_exercise_assignments?assignment_id=1")
    data = rv.get_json()["patient_exercise_assignments"]
    assert len(data) == 1 and data[0]["assignment_id"] == 1

def test_get_filter_by_patient_id(client):
    rv = client.get("/patient_exercise_assignments?patient_id=11")
    data = rv.get_json()["patient_exercise_assignments"]
    assert len(data) == 1 and data[0]["patient_id"] == 11

def test_get_filter_by_doctor_id(client):
    rv = client.get("/patient_exercise_assignments?doctor_id=21")
    data = rv.get_json()["patient_exercise_assignments"]
    assert len(data) == 1 and data[0]["doctor_id"] == 21

def test_get_filter_by_exercise_id(client):
    rv = client.get("/patient_exercise_assignments?exercise_id=31")
    data = rv.get_json()["patient_exercise_assignments"]
    assert len(data) == 1 and data[0]["exercise_id"] == 31

def test_get_filter_by_assigned_at(client):
    snippet = datetime.utcnow().strftime("%Y-%m-%d")
    rv = client.get(f"/patient_exercise_assignments?assigned_at={snippet}")
    data = rv.get_json()["patient_exercise_assignments"]
    assert all(snippet in item["assigned_at"] for item in data)

def test_post_missing_fields(client):
    payload = {"patient_id":99, "exercise_id":88}
    rv = client.post("/patient_exercise_assignments", json=payload)
    assert rv.status_code == 400
    assert b"Missing required fields" in rv.data

def test_post_success(client):
    payload = {
        "patient_id":100,
        "doctor_id":200,
        "exercise_id":300,
        "frequency_per_week":5,
        "reps":12,
        "sets":3
    }
    rv = client.post("/patient_exercise_assignments", json=payload)
    assert rv.status_code == 201
    assert b"created successfully" in rv.data
    all_rows = client.get("/patient_exercise_assignments").get_json()["patient_exercise_assignments"]
    assert any(r["patient_id"] == 100 and r["frequency_per_week"] == 5 for r in all_rows)

def test_patch_not_found(client):
    rv = client.patch("/patient_exercise_assignments/999", json={"reps":20})
    assert rv.status_code == 404
    assert b"not found" in rv.data

def test_patch_no_fields(client):
    rv = client.patch("/patient_exercise_assignments/1", json={})
    assert rv.status_code == 400
    assert b"No update fields provided" in rv.data

def test_patch_success(client):
    rv = client.patch("/patient_exercise_assignments/1", json={"reps":99, "sets":9})
    assert rv.status_code == 200
    assert b"updated successfully" in rv.data

    updated = client.get("/patient_exercise_assignments?assignment_id=1").get_json()["patient_exercise_assignments"][0]
    assert updated["reps"] == 99 and updated["sets"] == 9

def test_delete_not_found(client):
    rv = client.delete("/patient_exercise_assignments/999")
    assert rv.status_code == 400

def test_delete_success(client):
    rv = client.delete("/patient_exercise_assignments/1")
    assert rv.status_code == 200
    remaining = client.get("/patient_exercise_assignments").get_json()["patient_exercise_assignments"]
    assert all(r["assignment_id"] != 1 for r in remaining)
