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
        SECRET_KEY='test-secret',
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        LOGIN_DISABLED=True
    )
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS saved_posts"))
        db.session.execute(text("DROP TABLE IF EXISTS forum_posts"))
        db.session.execute(text("DROP TABLE IF EXISTS users"))
        db.session.execute(text("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL
            )
        """))
        db.session.execute(text("""
            CREATE TABLE forum_posts (
                post_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL
            )
        """))
        db.session.execute(text("""
            CREATE TABLE saved_posts (
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                saved_at TEXT NOT NULL
            )
        """))
        db.session.execute(text("""
            INSERT INTO users (user_id, first_name, last_name)
            VALUES (1, 'Alice', 'Smith'), (2, 'Bob', 'Jones')
        """))
        db.session.execute(text("""
            INSERT INTO forum_posts (post_id, title)
            VALUES (10, 'Post One'), (20, 'Post Two')
        """))
        db.session.execute(text("""
            INSERT INTO saved_posts (user_id, post_id, saved_at)
            VALUES (1, 10, '2025-04-23'), (2, 20, '2025-04-23')
        """))
        db.session.commit()
    with app.test_client() as c:
        yield c


def test_get_all_saved_posts(client):
    resp = client.get('/saved_posts')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data.get('saved_posts'), list)
    assert any(item['user_id'] == 1 for item in data['saved_posts'])

    entry = next((i for i in data['saved_posts'] if i['user_id'] == 1), {})
    assert 'Alice' in entry.get('first_name', '')
    assert 'Smith' in entry.get('last_name', '')
    assert entry.get('post_id') == 10
    assert 'Post' in entry.get('title', '')
    assert entry.get('saved_at', '').startswith('2025-04-2')


def test_filter_by_user_id(client):
    resp = client.get('/saved_posts?user_id=2')
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(p['user_id'] == 2 for p in data['saved_posts'])


def test_filter_by_post_id(client):
    resp = client.get('/saved_posts?post_id=10')
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(p['post_id'] == 10 for p in data['saved_posts'])


def test_filter_by_saved_at(client):
    resp = client.get('/saved_posts?saved_at=2025-04-23')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data.get('saved_posts'), list)
    for entry in data['saved_posts']:
        assert entry.get('saved_at', '').startswith('2025-04-2')


def test_delete_saved_post_nonexistent(client):
    payload = {'post_id': 999, 'user_id': 999}
    resp = client.delete('/saved_posts', json=payload)
    assert resp.status_code in [400, 404]


def test_delete_saved_post_success(client):
    payload = {'post_id': 10, 'user_id': 1}
    resp = client.delete('/saved_posts', json=payload)
    assert resp.status_code in [200, 204]

    resp2 = client.get('/saved_posts?user_id=1&post_id=10')
    data2 = resp2.get_json()
    assert all(p['user_id'] != 1 or p['post_id'] != 10 for p in data2['saved_posts'])


def test_add_saved_post_missing_params(client):
    payload = {'user_id': 1}
    resp = client.post('/saved_posts', json=payload)
    assert resp.status_code in [400, 422]


def test_add_saved_post_success(client):
    payload = {'user_id': 1, 'post_id': 20}
    resp = client.post('/saved_posts', json=payload)
    assert resp.status_code in [200, 201]

    resp2 = client.get('/saved_posts?user_id=1&post_id=20')
    data2 = resp2.get_json()
    assert any(p['user_id'] == 1 and p['post_id'] == 20 for p in data2['saved_posts'])
