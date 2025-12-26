import sqlite3
from datetime import datetime

async def insert_message(db, payload):
    try:
        await db.execute(
            """
            INSERT INTO messages
            (message_id, from_msisdn, to_msisdn, ts, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload["message_id"],
                payload["from"],
                payload["to"],
                payload["ts"],
                payload.get("text"),
                datetime.utcnow().isoformat() + "Z"
            )
        )
        await db.commit()
        return "created"
    except sqlite3.IntegrityError:
        return "duplicate"
