import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask import Response
from sqlalchemy import text
from datetime import datetime, timedelta, timezone

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

        db.session.execute(text("DROP TABLE IF EXISTS patients"))
        db.session.execute(text("""
            CREATE TABLE patients (
                patient_id INTEGER PRIMARY KEY
            )
        """))

        db.session.execute(text("DROP TABLE IF EXISTS patient_progress"))
        db.session.execute(text("""
            CREATE TABLE patient_progress (
                progress_id INTEGER PRIMARY KEY,
                patient_id  INTEGER NOT NULL,
                weight      REAL    NOT NULL,
                calories    INTEGER NOT NULL,
                water_intake TEXT,
                date_logged TEXT    NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
            )
        """))

        db.session.execute(text("INSERT INTO patients (patient_id) VALUES (42)"))
        now = datetime.now(timezone.utc)
        for idx, days in enumerate((0, 1), start=1):
            logged = (now - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            db.session.execute(text("""
                INSERT INTO patient_progress
                  (progress_id, patient_id, weight, calories, water_intake, date_logged)
                VALUES (:pid, 42, :wt, :cal, :water_intake, :logged)
            """), {
                "pid": idx,
                "wt": 180.0 - idx,
                "cal": 2000 + idx * 100,
                "water_intake": f"Entry {idx}",
                "logged": logged
            })
        db.session.commit()

    with app.test_client() as c:
        yield c

def test_get_all_progress(client):
    rv = client.get("/patient_progress")
    assert rv.status_code == 200
    data = rv.get_json()["patient_progress"]
    assert len(data) == 2
    assert data[0]["progress_id"] == 1

def test_get_filter_by_progress_id(client):
    rv = client.get("/patient_progress?progress_id=2")
    assert rv.status_code == 200
    arr = rv.get_json()["patient_progress"]
    assert len(arr) == 1 and arr[0]["progress_id"] == 2

def test_get_filter_by_patient_id(client):
    rv = client.get("/patient_progress?patient_id=42")
    assert rv.status_code == 200
    assert len(rv.get_json()["patient_progress"]) == 2

def test_get_filter_by_date_logged(client):
    full_date = client.get("/patient_progress").get_json()["patient_progress"][0]["date_logged"]
    rv = client.get(f"/patient_progress?date_logged={full_date}")
    assert rv.status_code == 200
    assert all(full_date == p["date_logged"] for p in rv.get_json()["patient_progress"])


def test_delete_nonexistent_progress(client):
    rv = client.delete("/patient_progress/999")
    assert rv.status_code == 400

def test_delete_existing_progress(client):
    rv = client.delete("/patient_progress/1")
    assert rv.status_code == 200
    all_after = client.get("/patient_progress").get_json()["patient_progress"]
    assert all(p["progress_id"] != 1 for p in all_after)

def test_post_missing_parameters(client):
    payload = {"patient_id": 42, "calories": 2100}
    rv = client.post("/patient_progress", json=payload)
    assert rv.status_code == 400
    assert b"Required parameters not supplied" in rv.data


@pytest.mark.parametrize("field,value,msg", [
    ("patient_id", 999, b"Invalid patient id"),
    ("weight", 0,      b"Invalid weight"),
    ("weight", 2000,   b"Invalid weight"),
    ("calories", 0,    b"Invalid calories"),
    ("calories", 50000, b"Invalid calories"),
])
def test_post_validation_errors(client, field, value, msg):
    payload = {
        "patient_id": 42,
        "weight": 175.0,
        "calories": 2200,
        "water_intake": "Test"
    }
    payload[field] = value
    rv = client.post("/patient_progress", json=payload)
    assert rv.status_code == 400
    assert msg in rv.data

def test_post_success(client):
    payload = {
        "patient_id": 42,
        "weight": 174.5,
        "calories": 2150,
        "water_intake": "New entry"
    }
    rv = client.post("/patient_progress", json=payload)
    assert rv.status_code == 201
    assert b"patient progress entry successfully created" in rv.data
    all_rows = client.get("/patient_progress").get_json()["patient_progress"]
    assert any(r["water_intake"] == "New entry" for r in all_rows)
