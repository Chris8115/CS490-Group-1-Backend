import os
import sys
import pytest
from sqlalchemy import text
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app, db

@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        LOGIN_DISABLED=True
    )
    with app.app_context():
        db.session.execute(text("DROP TABLE IF EXISTS exercise_plans"))
        db.session.execute(text("""
            CREATE TABLE exercise_plans (
                exercise_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT
            )
        """))
        db.session.execute(text("""
            INSERT INTO exercise_plans (exercise_id, title, description)
            VALUES (1, 'Stretch Routine', 'Full body warm-up')
        """))
        db.session.commit()
    with app.test_client() as c:
        yield c

def test_get_all_exercise_plans(client):
    resp = client.get('/exercise_plans')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'exercise_plans' in data
    assert len(data['exercise_plans']) == 1

def test_get_filtered_exercise_plans(client):
    resp = client.get('/exercise_plans?exercise_id=1')
    assert resp.status_code == 200
    data = resp.get_json()['exercise_plans']
    assert len(data) == 1
    assert data[0]['title'] == 'Stretch Routine'

    resp_none = client.get('/exercise_plans?exercise_id=999')
    assert resp_none.status_code == 200
    assert resp_none.get_json()['exercise_plans'] == []

def test_delete_nonexistent_exercise_plan(client):
    resp = client.delete('/exercise_plans/999')
    assert resp.status_code == 400

def test_delete_existing_exercise_plan(client):
    resp = client.delete('/exercise_plans/1')
    assert resp.status_code == 200
    check = client.get('/exercise_plans').get_json()['exercise_plans']
    assert check == []
