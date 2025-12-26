import time
import hmac
import hashlib
import aiosqlite
from fastapi import FastAPI, Request, HTTPException
from prometheus_client import generate_latest

from app.config import settings
from app.models import init_db
from app.storage import insert_message
from app.logging_utils import log_request
from app.metrics import http_requests_total, webhook_requests_total, request_latency_ms

app = FastAPI()

def verify_signature(secret: str, body: bytes, signature: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.get("/health/live")
def health_live():
    return {"status": "live"}

@app.get("/health/ready")
async def health_ready():
    if not settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=503)

    try:
        async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "/")) as db:
            await init_db(db)
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503)

@app.post("/webhook")
async def webhook(request: Request):
    start = time.time()
    body = await request.body()
    signature = request.headers.get("X-Signature")

    if not signature or not verify_signature(settings.WEBHOOK_SECRET, body, signature):
        webhook_requests_total.labels(result="invalid_signature").inc()
        http_requests_total.labels(path="/webhook", status="401").inc()
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = await request.json()

    async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "/")) as db:
        result = await insert_message(db, payload)

    webhook_requests_total.labels(result=result).inc()
    http_requests_total.labels(path="/webhook", status="200").inc()
    request_latency_ms.observe((time.time() - start) * 1000)

    log_request(
        level="INFO",
        method="POST",
        path="/webhook",
        status=200,
        latency_ms=int((time.time() - start) * 1000),
        message_id=payload.get("message_id"),
        dup=result == "duplicate",
        result=result
    )

    return {"status": "ok"}

@app.get("/messages")
async def get_messages(limit: int = 50, offset: int = 0):
    async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "/")) as db:
        rows = await (await db.execute(
            """
            SELECT message_id, from_msisdn, to_msisdn, ts, text
            FROM messages
            ORDER BY ts ASC, message_id ASC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )).fetchall()

        total = (await (await db.execute(
            "SELECT COUNT(*) FROM messages"
        )).fetchone())[0]

    return {
        "data": [
            {
                "message_id": r[0],
                "from": r[1],
                "to": r[2],
                "ts": r[3],
                "text": r[4]
            } for r in rows
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/stats")
async def stats():
    async with aiosqlite.connect(settings.DATABASE_URL.replace("sqlite:///", "/")) as db:
        total = (await (await db.execute(
            "SELECT COUNT(*) FROM messages"
        )).fetchone())[0]

        senders = await (await db.execute(
            """
            SELECT from_msisdn, COUNT(*)
            FROM messages
            GROUP BY from_msisdn
            ORDER BY COUNT(*) DESC
            LIMIT 10
            """
        )).fetchall()

        first_last = await (await db.execute(
            "SELECT MIN(ts), MAX(ts) FROM messages"
        )).fetchone()

    return {
        "total_messages": total,
        "senders_count": len(senders),
        "messages_per_sender": [
            {"from": s[0], "count": s[1]} for s in senders
        ],
        "first_message_ts": first_last[0],
        "last_message_ts": first_last[1]
    }

@app.get("/metrics")
def metrics():
    return generate_latest()
