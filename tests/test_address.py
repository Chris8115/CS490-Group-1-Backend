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
        db.session.execute(text("DROP TABLE IF EXISTS address"))
        db.session.execute(text("""
            CREATE TABLE address (
                address_id INTEGER PRIMARY KEY,
                city TEXT, country TEXT, address2 TEXT,
                address TEXT, state TEXT, zip TEXT
            )
        """))
        db.session.execute(text("""
            INSERT INTO address (address_id, city, country, address2, address, state, zip)
            VALUES (1, 'Springfield', 'USA', 'Apt 2B', '742 Evergreen Terrace', 'IL', '62704')
        """))
        db.session.commit()
    with app.test_client() as c:
        yield c

def test_get_all_addresses(client):
    resp = client.get("/address")
    assert resp.status_code == 200
    data = resp.get_json()["address"]
    assert len(data) == 1
    assert data[0]["city"] == "Springfield"

def test_get_by_city(client):
    resp = client.get("/address?city=Spring")
    assert resp.status_code == 200
    assert len(resp.get_json()["address"]) == 1

def test_patch_not_found(client):
    resp = client.patch("/address/999", json={"city": "Nowhere"})
    assert resp.status_code == 404
    assert b"Address not found" in resp.data

def test_patch_success(client):
    resp = client.patch("/address/1", json={"city": "Shelbyville"})
    assert resp.status_code == 200
    assert b"Address updated successfully" in resp.data

def test_patch_no_fields(client):
    resp = client.patch("/address/1", json={})
    assert resp.status_code == 400
    assert b"No update fields provided" in resp.data

def test_delete_success(client):
    resp = client.delete("/address/1")
    assert resp.status_code == 200
    assert client.get("/address").get_json()["address"] == []

def test_delete_not_found(client):
    resp = client.delete("/address/999")
    assert resp.status_code == 400
