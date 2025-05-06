import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import app, logout_user, login_manager

@pytest.fixture
# Disable login_required for tests
def client():
    app.config.update(
        TESTING=True,
        SECRET_KEY='test-secret',
        LOGIN_DISABLED=True
    )
    with app.test_client() as c:
        yield c

@pytest.mark.parametrize('method', ['get', 'post'])
def test_logout_calls_logout_user_and_returns_200(client, monkeypatch, method):
    # Monkey-patch logout_user to record invocation
    called = []
    monkeypatch.setattr('app.logout_user', lambda: called.append(True))

    # Call logout endpoint via GET or POST
    if method == 'get':
        resp = client.get('/logout')
    else:
        resp = client.post('/logout')

    assert resp.status_code == 200
    assert b"User Logged out" in resp.data
    assert called, "logout_user() was not called"


def test_logout_route_registered():
    # Ensure the logout route exists
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert '/logout' in rules

def test_login_check_returns_user_id(client, monkeypatch):
    from flask_login import utils

    class DummyUser:
        def __init__(self):
            self.user_id = 42
            self.role = 'patient'
            self.email='email@gmail.com'

        def get_id(self):
            return str(self.user_id)

    monkeypatch.setattr(utils, "_get_user", lambda: DummyUser())

    resp = client.get('/login_check')
    assert resp.status_code == 200
    assert b"User is logged in. ID: 42" in resp.data


def test_login_check_route_registered():
    # Ensure the login_check route exists
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert '/login_check' in rules
