from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_messages_endpoint():
    res = client.get("/messages")
    assert res.status_code == 200
    assert "data" in res.json()
