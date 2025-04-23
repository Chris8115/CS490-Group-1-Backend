import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy import text
from app import app, db

@pytest.fixture
def client():
    # Configure Flask test client and disable login_required
    app.config.update(
        TESTING=True,
        SECRET_KEY='test-secret',
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        LOGIN_DISABLED=True
    )
    with app.app_context():
        # Drop tables if they already exist
        db.session.execute(text("DROP TABLE IF EXISTS saved_posts"))
        db.session.execute(text("DROP TABLE IF EXISTS forum_posts"))
        db.session.execute(text("DROP TABLE IF EXISTS users"))
        # Create users table
        db.session.execute(text(
            """
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL
            )
            """
        ))
        # Create forum_posts table
        db.session.execute(text(
            """
            CREATE TABLE forum_posts (
                post_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL
            )
            """
        ))
        # Create saved_posts table
        db.session.execute(text(
            """
            CREATE TABLE saved_posts (
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                saved_at TEXT NOT NULL
            )
            """
        ))
        # Seed data
        db.session.execute(text(
            "INSERT INTO users (user_id, first_name, last_name) VALUES (1, 'Alice', 'Smith'), (2, 'Bob', 'Jones')"
        ))
        db.session.execute(text(
            "INSERT INTO forum_posts (post_id, title) VALUES (10, 'Post One'), (20, 'Post Two')"
        ))
        db.session.execute(text(
            "INSERT INTO saved_posts (user_id, post_id, saved_at) VALUES (1, 10, '2025-04-23'), (2, 20, '2025-04-22')"
        ))
        db.session.commit()
    with app.test_client() as c:
        yield c


def test_get_all_saved_posts(client):
    resp = client.get('/saved_posts')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'saved_posts' in data
    assert len(data['saved_posts']) == 2
    # verify one entry
    entry = next(item for item in data['saved_posts'] if item['user_id'] == 1)
    assert entry['first_name'] == 'Alice'
    assert entry['last_name'] == 'Smith'
    assert entry['post_id'] == 10
    assert entry['title'] == 'Post One'
    assert entry['saved_at'] == '2025-04-23'


def test_filter_by_user_id(client):
    resp = client.get('/saved_posts?user_id=2')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['saved_posts']) == 1
    assert data['saved_posts'][0]['user_id'] == 2
    assert data['saved_posts'][0]['first_name'] == 'Bob'


def test_filter_by_post_id(client):
    resp = client.get('/saved_posts?post_id=10')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['saved_posts']) == 1
    assert data['saved_posts'][0]['post_id'] == 10


def test_filter_by_saved_at(client):
    resp = client.get('/saved_posts?saved_at=2025-04-22')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data['saved_posts']) == 1
    assert data['saved_posts'][0]['saved_at'] == '2025-04-22'

# DELETE /saved_posts endpoint tests

def test_delete_saved_post_nonexistent(client):
    # Attempt to delete a non-existent saved post
    payload = {'post_id': 999, 'user_id': 999}
    resp = client.delete('/saved_posts', json=payload)
    assert resp.status_code == 400


def test_delete_saved_post_success(client):
    # Delete an existing saved post
    payload = {'post_id': 10, 'user_id': 1}
    resp = client.delete('/saved_posts', json=payload)
    assert resp.status_code == 200
    # Ensure it is actually deleted
    resp2 = client.get('/saved_posts?user_id=1&post_id=10')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert len(data2['saved_posts']) == 0

    # POST /saved_posts endpoint tests
def test_add_saved_post_missing_params(client):
    # Missing post_id should return 400
    payload = {'user_id': 1}
    resp = client.post('/saved_posts', json=payload)
    assert resp.status_code == 400
    assert b"Required parameters not supplied" in resp.data


def test_add_saved_post_success(client):
    # Add a new saved post
    payload = {'user_id': 1, 'post_id': 20}
    resp = client.post('/saved_posts', json=payload)
    assert resp.status_code == 201
    assert b"Post saved successfully" in resp.data
    # Confirm via GET filter
    resp2 = client.get('/saved_posts?user_id=1&post_id=20')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert len(data2['saved_posts']) == 1
    entry = data2['saved_posts'][0]
    assert entry['user_id'] == 1
    assert entry['post_id'] == 20

