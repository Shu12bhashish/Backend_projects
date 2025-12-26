from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_stats_endpoint():
    res = client.get("/stats")
    assert res.status_code == 200
    assert "total_messages" in res.json()
