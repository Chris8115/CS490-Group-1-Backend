# tests/test_transactions.py

import os
import sys
# Make sure we can import app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import datetime
from sqlalchemy import text
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['LOGIN_DISABLED'] = True 

    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS transactions"))
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

        dummy_ts = datetime(2025, 4, 17, 12, 0, 0).strftime("%Y-%m-%d 12:00:00")
        db.session.execute(text("""
            INSERT INTO transactions (
              creditcard_id, doctor_id, patient_id,
              service_fee, doctor_fee, subtotal,
              created_at, transaction_id
            ) VALUES (
              :cc, :dr, :pt,
              :sf, :df, :st,
              :ts, :tid
            )
        """), {
            'cc': 42,
            'dr': 99,
            'pt': 123,
            'sf': '1.23',
            'df': '4.56',
            'st': '5.79',
            'ts': dummy_ts,
            'tid': 9001
        })
        db.session.commit()

    with app.test_client() as c:
        yield c

def test_get_all_transactions(client):
    resp = client.get('/transactions')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'transactions' in data
    assert len(data['transactions']) == 1

def test_get_seeded_transaction_fields(client):
    tx = client.get('/transactions').get_json()['transactions'][0]
    assert tx['creditcard_id'] == 42
    assert tx['doctor_id']    == 99
    assert tx['patient_id']   == 123
    assert tx['transaction_id'] == 9001
    assert tx['service_fee']  == '1.23'
    assert tx['doctor_fee']   == '4.56'
    assert tx['subtotal']     == '5.79'

def test_filter_by_creditcard_id(client):
    resp = client.get('/transactions?creditcard_id=42')
    assert resp.status_code == 200
    assert len(resp.get_json()['transactions']) == 1

    resp = client.get('/transactions?creditcard_id=999')
    assert resp.status_code == 200
    assert resp.get_json()['transactions'] == []

# Deleting a non-existent transaction should return 400
def test_delete_nonexistent_transaction(client):
    resp = client.delete('/transactions/999')
    assert resp.status_code == 400

# Successfully delete an existing transaction
def test_delete_transaction_success(client):
    resp = client.delete('/transactions/9001')
    assert resp.status_code == 200

    resp2 = client.delete('/transactions/9001')
    assert resp2.status_code == 400

