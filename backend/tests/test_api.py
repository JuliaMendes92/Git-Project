import pytest
from fastapi.testclient import TestClient
from app import main
from passlib.context import CryptContext
import pandas as pd

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(autouse=True)
def setup_data(tmp_path, monkeypatch):
    # create small users and metrics dataframes
    users = pd.DataFrame([
        {"email":"admin@example.com","full_name":"Admin","role":"admin","password_hash": pwd.hash("adminpass")},
        {"email":"user@example.com","full_name":"User","role":"user","password_hash": pwd.hash("userpass")},
    ])
    metrics = pd.DataFrame([
        {"account_id":1, "date":pd.to_datetime('2025-09-01'), "impressions":1000, "clicks":50, "conversions":5, "cost_micros":1230000},
        {"account_id":2, "date":pd.to_datetime('2025-09-02'), "impressions":2000, "clicks":100, "conversions":10, "cost_micros":2500000},
    ])
    # monkeypatch the dataframes in main
    monkeypatch.setattr(main, 'users_df', users)
    monkeypatch.setattr(main, 'metrics_df', metrics)
    return


def test_login_success_and_metrics_admin():
    client = TestClient(main.app)
    # login as admin
    r = client.post('/token', data={'username':'admin@example.com','password':'adminpass'})
    assert r.status_code == 200
    token = r.json()['access_token']

    # get metrics
    r2 = client.get('/metrics', headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200
    data = r2.json()
    assert 'data' in data
    # admin should see cost_micros
    assert 'cost_micros' in data['data'][0]


def test_login_user_cannot_see_cost():
    client = TestClient(main.app)
    r = client.post('/token', data={'username':'user@example.com','password':'userpass'})
    assert r.status_code == 200
    token = r.json()['access_token']

    r2 = client.get('/metrics', headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200
    data = r2.json()
    assert 'data' in data
    assert 'cost_micros' not in data['data'][0]


def test_filter_by_date():
    client = TestClient(main.app)
    r = client.post('/token', data={'username':'admin@example.com','password':'adminpass'})
    token = r.json()['access_token']
    # filter to a date with only one row
    r2 = client.get('/metrics', params={'start_date':'2025-09-02','end_date':'2025-09-02'}, headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200
    data = r2.json()
    assert len(data['data']) == 1
