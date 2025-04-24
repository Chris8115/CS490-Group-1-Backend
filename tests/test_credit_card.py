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
        db.session.execute(text("DROP TABLE IF EXISTS credit_card"))
        db.session.execute(text("""
            CREATE TABLE credit_card (
              creditcard_id INTEGER PRIMARY KEY,
              cardnumber    TEXT NOT NULL,
              exp_date      TEXT NOT NULL,
              cvv           TEXT NOT NULL
            )
        """))
        db.session.execute(text("""
            INSERT INTO credit_card (creditcard_id, cardnumber, exp_date, cvv)
            VALUES (1, '4111111111111111', '2025-12-31', '123')
        """))
        db.session.commit()
    with app.test_client() as c:
        yield c

def test_get_credit_cards(client):
    rv = client.get("/credit_card")
    assert rv.status_code == 200
    data = rv.get_json()["credit_card"]
    assert len(data) == 1
    assert data[0]["card_ending"].endswith("1111")

def test_get_credit_cards_filtered_by_id(client):
    rv = client.get("/credit_card?creditcard_id=1")
    assert rv.status_code == 200
    assert len(rv.get_json()["credit_card"]) == 1

def test_get_credit_cards_filtered_too_long(client):
    rv = client.get("/credit_card?card_ending=123456")
    assert rv.status_code == 400
    assert b"Card ending query cannot exceed 4 characters" in rv.data

def test_patch_invalid_format(client):
    assert client.patch("/credit_card/1", json={"cardnumber": "abcd"}).status_code == 400
    assert client.patch("/credit_card/1", json={"cvv": "12"}).status_code == 400
    assert client.patch("/credit_card/1", json={"exp_date": "12-31-2025"}).status_code == 400

def test_patch_successful_update(client):
    rv = client.patch("/credit_card/1", json={
        "cardnumber": "4222222222222222",
        "exp_date": "2026-01-01",
        "cvv": "456"
    })
    assert rv.status_code == 200
    assert b"Credit card updated successfully" in rv.data

def test_patch_no_fields(client):
    rv = client.patch("/credit_card/1", json={})
    assert rv.status_code == 400
    assert b"No update fields provided" in rv.data

def test_patch_card_not_found(client):
    rv = client.patch("/credit_card/999", json={"cvv": "123"})
    assert rv.status_code == 404
    assert b"Credit card not found" in rv.data

def test_delete_credit_card_success(client):
    rv = client.delete("/credit_card/1")
    assert rv.status_code == 200

def test_delete_credit_card_not_found(client):
    rv = client.delete("/credit_card/999")
    assert rv.status_code == 400
