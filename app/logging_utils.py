import json
import uuid
from datetime import datetime

def log_request(**kwargs):
    log = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "request_id": str(uuid.uuid4()),
        **kwargs
    }
    print(json.dumps(log))
