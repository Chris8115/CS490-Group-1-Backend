import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import text
from app import app, db, Users, login_user, logout_user, current_user

# Monkeypatch login_user to avoid real session logic

def dummy_login(user, remember=False):
    pass

@pytest.fixture(autouse=True)
def patch_login_user(monkeypatch):
    monkeypatch.setattr('app.login_user', dummy_login)

@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SECRET_KEY='test-secret',
        MAIL_SUPPRESS_SEND=True
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = Users(
            user_id=1,
            email='test123@example.com',
            password='pass',
            first_name='Test',
            last_name='User',
            phone_number=1234567890,
            role='patient',
            eula=True,
            created_at='2025-01-01'
        )
        db.session.add(user)
        db.session.commit()
    with app.test_client() as c:
        yield c

# GET /login missing credentials

def test_get_missing_credentials(client):
    resp = client.get('/login')
    assert resp.status_code == 400
    assert b"Required credentials not sent" in resp.data

# POST /login missing credentials

def test_post_missing_credentials(client):
    resp = client.post('/login', json={})
    assert resp.status_code == 400
    assert b"Required credentials not sent" in resp.data

# Invalid email format
@pytest.mark.parametrize('method', ['get', 'post'])
def test_invalid_email_format(client, method):
    if method == 'get':
        resp = client.get('/login?email=invalid&password=anything')
    else:
        resp = client.post('/login', json={'email': 'invalid', 'password': 'pw'})
    assert resp.status_code == 400
    assert b"Invalid email address" in resp.data

# User not found
@pytest.mark.parametrize('method', ['get', 'post'])
def test_invalid_user_credentials(client, method):
    if method == 'get':
        resp = client.get('/login?email=noone@example.com&password=whatever')
    else:
        resp = client.post('/login', json={'email': 'noone@example.com', 'password': 'whatever'})
    assert resp.status_code == 401
    assert b"Invalid user credentials" in resp.data

# Wrong password
@pytest.mark.parametrize('method', ['get', 'post'])
def test_invalid_password(client, method):
    if method == 'get':
        resp = client.get('/login?email=test123@example.com&password=wrong')
    else:
        resp = client.post('/login', json={'email': 'test123@example.com', 'password': 'wrong'})
    assert resp.status_code == 401
    assert b"Invalid password" in resp.data

# Successful login
@pytest.mark.parametrize('method', ['get', 'post'])
def test_successful_login(client, monkeypatch, method):
    # Patch current_user after dummy login
    with app.app_context():
        user = db.session.get(Users, 1)
    monkeypatch.setattr('app.current_user', user)
    if method == 'get':
        resp = client.get('/login?email=test123@example.com&password=pass&remember=1')
    else:
        resp = client.post('/login', json={'email': 'test123@example.com', 'password': 'pass', 'remember': True})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['user_id'] == 1
    assert data['role'] == 'patient'
    assert 'Login successful' in data.get('message', '')


# Route registration and decorator coverage
def test_route_registration():
    import app as _app
    rules = {rule.rule for rule in _app.app.url_map.iter_rules()}
    assert '/login' in rules
