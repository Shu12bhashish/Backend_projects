import hmac
import hashlib
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def sign(body: bytes):
    return hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

def test_invalid_signature():
    body = b'{"message_id":"m1","from":"+91","to":"+1","ts":"2025-01-01T00:00:00Z"}'
    res = client.post("/webhook", data=body, headers={"X-Signature": "bad"})
    assert res.status_code == 401

def test_valid_and_duplicate():
    body = b'{"message_id":"m2","from":"+91","to":"+1","ts":"2025-01-01T01:00:00Z"}'
    sig = sign(body)

    r1 = client.post("/webhook", data=body, headers={"X-Signature": sig})
    r2 = client.post("/webhook", data=body, headers={"X-Signature": sig})

    assert r1.status_code == 200
    assert r2.status_code == 200
