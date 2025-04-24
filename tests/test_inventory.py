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
        db.session.execute(text("DROP TABLE IF EXISTS inventory"))
        db.session.execute(text("""
            CREATE TABLE inventory (
                inventory_id INTEGER PRIMARY KEY,
                medication_id INTEGER NOT NULL,
                stock INTEGER NOT NULL,
                last_updated TEXT NOT NULL
            )
        """))
        db.session.execute(text("""
            INSERT INTO inventory (inventory_id, medication_id, stock, last_updated)
            VALUES (1, 10, 50, '2025-04-23 12:00:00')
        """))
        db.session.commit()

    with app.test_client() as c:
        yield c

def test_get_all_inventory(client):
    resp = client.get('/inventory')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['inventory']) == 1
    assert data['inventory'][0]['inventory_id'] == 1

def test_get_filtered_inventory(client):
    resp = client.get('/inventory?inventory_id=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['inventory']) == 1
    assert data['inventory'][0]['stock'] == 50

    resp = client.get('/inventory?inventory_id=999')
    assert resp.status_code == 200
    assert resp.get_json()['inventory'] == []

def test_delete_nonexistent_inventory(client):
    resp = client.delete('/inventory/999')
    assert resp.status_code == 400

def test_delete_inventory_success(client):
    resp = client.delete('/inventory/1')
    assert resp.status_code == 200

    resp2 = client.get('/inventory')
    assert resp2.get_json()['inventory'] == []
