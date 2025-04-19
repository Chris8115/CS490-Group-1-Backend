import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask_mail import Message
from sqlalchemy import text
from app import app, db, mail

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['MAIL_SUPPRESS_SEND'] = True   # Prevent real emails

    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS users"))
        db.session.execute(text("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                email   TEXT    NOT NULL
            )
        """))
        db.session.execute(text("""
            INSERT INTO users (user_id, email)
            VALUES (1, 'test@example.com')
        """))
        db.session.commit()

    with app.test_client() as c:
        yield c

# Check if there's no user
def test_invalid_user_id(client):
    resp = client.post('/mail/999', json={
        'email_subject': 'Hi',
        'email_body': 'Hello'
    })
    assert resp.status_code == 400
    assert b"Invalid user" in resp.data

# Check missing body
def test_missing_email_body(client):
    resp = client.post('/mail/1', json={
        'email_subject': 'Subject Only'
    })
    assert resp.status_code == 400
    assert b"No email body" in resp.data

# Check empty body (almost forgot this distinction)
def test_empty_email_body(client):
    resp = client.post('/mail/1', json={
        'email_body': '',
        'email_subject': 'Hello'
    })
    assert resp.status_code == 400
    assert b"No email body" in resp.data

# Check missing subject
def test_missing_email_subject(client):
    resp = client.post('/mail/1', json={
        'email_body': 'Body Only'
    })
    assert resp.status_code == 400
    assert b"No email subject" in resp.data

# Check empty subject
def test_empty_email_subject(client):
    resp = client.post('/mail/1', json={
        'email_body': 'Hello',
        'email_subject': ''
    })
    assert resp.status_code == 400
    assert b"No email subject" in resp.data

# Check if it actually sent
def test_successful_email_send(client, monkeypatch):
    sent = {}
    def fake_send(msg):
        sent['msg'] = msg
        return True
    monkeypatch.setattr(mail, 'send', fake_send)

    resp = client.post('/mail/1', json={
        'email_subject': 'Greetings',
        'email_body': 'This is a test'
    })
    assert resp.status_code == 200
    assert b"Email sent to test@example.com" in resp.data

    msg = sent.get('msg')
    assert isinstance(msg, Message)
    assert msg.subject   == 'Greetings'
    assert msg.body      == 'This is a test'
    assert msg.sender    == 'betteru490@gmail.com'
    assert msg.recipients == ['test@example.com']

def test_route_is_registered():
    import app as _app
    rules = {rule.rule for rule in _app.app.url_map.iter_rules()}
    # Flask includes the converter type in the rule
    assert '/mail/<int:user_id>' in rules

def test_print_and_mail_send_side_effect(client, capsys, monkeypatch):
    def fake_send(msg):
        print(">> fake_send called with subject=", msg.subject)
        return None
    monkeypatch.setattr(mail, 'send', fake_send)

    resp = client.post('/mail/1', json={
        'email_subject': 'Hello!',
        'email_body': 'Capture this print'
    })
    assert resp.status_code == 200

    captured = capsys.readouterr()
    assert "fake_send called with subject=" in captured.out
    assert "Hello!" in captured.out
