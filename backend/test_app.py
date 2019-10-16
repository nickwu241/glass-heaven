import json

import pytest

from app import app


@pytest.fixture()
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    ctx = app.app_context()
    ctx.push()
    yield app.test_client()
    ctx.pop()


def test_index(test_client):
    r = test_client.get('/')
    assert r.status_code == 200
    assert b'companies' in r.data


def test_companies_get(test_client):
    r = test_client.get('/companies')
    assert r.status_code == 200
    json_data = json.loads(r.get_data(as_text=True))
    assert len(json_data) > 1


def test_companies_post(test_client):
    r = test_client.post('/companies', data=json.dumps({
        'companies': 'Airbnb,Google'
    }))
    assert r.status_code == 200
    json_data = json.loads(r.get_data(as_text=True))
    assert len(json_data) == 2
