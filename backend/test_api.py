from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)

def run_tests():
    print('GET /metrics without auth ->', client.get('/metrics').status_code)
    r = client.post('/token', data={'username':'admin@example.com','password':'wrong'})
    print('POST /token wrong ->', r.status_code, r.text)
    r2 = client.post('/token', data={'username':'admin@example.com','password':'adminpass'})
    print('POST /token adminpass ->', r2.status_code, r2.text)
    r3 = client.post('/token', data={'username':'user@example.com','password':'userpass'})
    print('POST /token userpass ->', r3.status_code, r3.text)

if __name__=='__main__':
    run_tests()
