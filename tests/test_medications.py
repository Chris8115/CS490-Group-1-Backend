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
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        LOGIN_DISABLED=True
    )
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS medications"))
        db.session.execute(text("""
            CREATE TABLE medications (
                medication_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            )
        """))
        db.session.execute(text("""
            INSERT INTO medications (medication_id, name, description)
            VALUES (1, 'Aspirin', 'Pain reliever')
        """))
        db.session.commit()
    with app.test_client() as c:
        yield c

def test_get_all_medications(client):
    rv = client.get("/medications")
    assert rv.status_code == 200
    meds = rv.get_json()["medications"]
    assert len(meds) == 1
    assert meds[0]["name"] == "Aspirin"

def test_get_medications_by_id(client):
    rv = client.get("/medications?medication_id=1")
    meds = rv.get_json()["medications"]
    assert len(meds) == 1
    assert meds[0]["medication_id"] == 1

def test_get_medications_by_name(client):
    rv = client.get("/medications?name=spir")
    meds = rv.get_json()["medications"]
    assert len(meds) == 1
    assert "Aspirin" in meds[0]["name"]

def test_get_medications_no_match(client):
    rv = client.get("/medications?name=xyz")
    meds = rv.get_json()["medications"]
    assert meds == []

def test_delete_medication_not_found(client):
    rv = client.delete("/medications/999")
    assert rv.status_code == 400

def test_delete_medication_success(client):
    rv = client.delete("/medications/1")
    assert rv.status_code == 200
    rv2 = client.get("/medications")
    assert rv2.get_json()["medications"] == []
