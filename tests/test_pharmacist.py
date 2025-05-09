import os
import sys
import pytest
from sqlalchemy import text
from app import app, db

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        LOGIN_DISABLED=True
    )
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS pharmacists"))
        db.session.execute(text("""
            CREATE TABLE pharmacists (
                pharmacist_id INTEGER PRIMARY KEY,
                pharmacy_location TEXT NOT NULL
            )
        """))
        db.session.execute(text("""
            INSERT INTO pharmacists (pharmacist_id, pharmacy_location)
            VALUES (1, 'Main St'), (2, 'Downtown Plaza')
        """))
        db.session.commit()
    with app.test_client() as c:
        yield c

# GET all
def test_get_all_pharmacists(client):
    res = client.get("/pharmacists")
    assert res.status_code == 200
    data = res.get_json()["pharmacists"]
    assert len(data) == 2

# GET filter by ID
def test_get_pharmacist_by_id(client):
    res = client.get("/pharmacists?pharmacist_id=1")
    data = res.get_json()["pharmacists"]
    assert len(data) == 1
    assert data[0]["pharmacist_id"] == 1

# GET filter by location (partial match)
def test_get_pharmacist_by_location(client):
    res = client.get("/pharmacists?pharmacy_location=Main")
    data = res.get_json()["pharmacists"]
    assert len(data) == 1
    assert "Main" in data[0]["pharmacy_location"]

# DELETE nonexistent
def test_delete_nonexistent_pharmacist(client):
    res = client.delete("/pharmacists/999")
    assert res.status_code == 400

# DELETE existing
def test_delete_existing_pharmacist(client):
    res = client.delete("/pharmacists/1")
    assert res.status_code == 200
    res2 = client.get("/pharmacists?pharmacist_id=1")
    assert res2.get_json()["pharmacists"] == []