import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import datetime
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
        db.session.execute(text("DROP TABLE IF EXISTS transactions"))
        db.session.execute(text("DROP TABLE IF EXISTS credit_card"))
        db.session.execute(text("DROP TABLE IF EXISTS patients"))
        db.session.execute(text("DROP TABLE IF EXISTS doctors"))

        db.session.execute(text("""
            CREATE TABLE transactions (
              creditcard_id   INTEGER NOT NULL,
              doctor_id       INTEGER NOT NULL,
              patient_id      INTEGER NOT NULL,
              service_fee     TEXT    NOT NULL,
              doctor_fee      TEXT    NOT NULL,
              subtotal        TEXT    NOT NULL,
              created_at      TEXT    NOT NULL,
              transaction_id  INTEGER PRIMARY KEY
            )
        """))
        db.session.execute(text("""
            CREATE TABLE credit_card (
              creditcard_id INTEGER PRIMARY KEY,
              cardnumber    TEXT    NOT NULL,
              exp_date      TEXT    NOT NULL,
              cvv           TEXT    NOT NULL
            )
        """))
        db.session.execute(text("CREATE TABLE patients (patient_id INTEGER PRIMARY KEY)"))
        db.session.execute(text("CREATE TABLE doctors (doctor_id INTEGER PRIMARY KEY)"))

        db.session.execute(text("""
            INSERT INTO credit_card (creditcard_id, cardnumber, exp_date, cvv)
            VALUES (1, '4111111111111111', '2025-12-31', '123')
        """))
        db.session.execute(text("INSERT INTO patients (patient_id) VALUES (100)"))
        db.session.execute(text("INSERT INTO doctors  (doctor_id)  VALUES (200)"))
        db.session.commit()

    with app.test_client() as c:
        yield c

def test_post_missing_parameters(client):
    payload = {
        "patient_id": 100,
        "doctor_id": 200,
        "service_fee": 5.00,
        "doctor_fee": 10.00,
        "subtotal": 15.00
        # Missing 'creditcard_number'
    }
    rv = client.post("/transactions", json=payload)
    assert rv.status_code == 400
    assert b"Required parameters not supplied" in rv.data


def test_post_invalid_credit_card(client):
    payload = {
        "patient_id": 100,
        "doctor_id": 200,
        "service_fee": 5.00,
        "doctor_fee": 10.00,
        "subtotal": 15.00,
        "creditcard_number": "0000000000000000"
    }
    rv = client.post("/transactions", json=payload)
    assert rv.status_code == 400
    assert b"Invalid credit card" in rv.data

def test_post_invalid_patient_id(client):
    payload = {
        "patient_id": 999,
        "doctor_id": 200,
        "service_fee": 5.00,
        "doctor_fee": 10.00,
        "subtotal": 15.00,
        "creditcard_number": "4111111111111111"
    }
    rv = client.post("/transactions", json=payload)
    assert rv.status_code == 400
    assert b"Invalid patient id" in rv.data

def test_post_invalid_doctor_id(client):
    payload = {
        "patient_id": 100,
        "doctor_id": 999,
        "service_fee": 5.00,
        "doctor_fee": 10.00,
        "subtotal": 15.00,
        "creditcard_number": "4111111111111111"
    }
    rv = client.post("/transactions", json=payload)
    assert rv.status_code == 400
    assert b"Invalid doctor id" in rv.data

@pytest.mark.parametrize("sf, df, st", [
    (-1.0,  5.0, 10.0),
    ( 5.0, -1.0, 10.0),
    ( 5.0,  5.0, -1.0),
])
def test_post_negative_fees(client, sf, df, st):
    payload = {
        "patient_id": 100,
        "doctor_id": 200,
        "service_fee": sf,
        "doctor_fee":  df,
        "subtotal":    st,
        "creditcard_number": "4111111111111111"
    }
    rv = client.post("/transactions", json=payload)
    assert rv.status_code == 400
    assert b"Fee or subtotal must be non negative" in rv.data

def test_post_successful_transaction(client):
    payload = {
        "patient_id": 100,
        "doctor_id": 200,
        "service_fee": 5.00,
        "doctor_fee": 10.00,
        "subtotal": 15.00,
        "creditcard_number": "4111111111111111"
    }
    rv = client.post("/transactions", json=payload)
    assert rv.status_code == 201
    assert b"Transaction record saved successfully" in rv.data

    all_tx = client.get("/transactions").get_json()["transactions"]
    assert len(all_tx) == 1
    tx = all_tx[0]
    assert tx["creditcard_id"] == 1
    assert tx["doctor_id"]     == 200
    assert tx["patient_id"]    == 100
