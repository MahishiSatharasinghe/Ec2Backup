from fastapi import FastAPI
from pydantic import BaseModel
from clickhouse_driver import Client
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime
import time
import logging

# ✅ Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Define event model
class TrackEvent(BaseModel):
    event_type: str
    page: str
    element: str = ""
    scroll_depth: float = 0
    duration: float = 0
    session_id: str

# ✅ Connect to ClickHouse with retry
for _ in range(10):
    try:
        client = Client(
            host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
            port=int(os.getenv("CLICKHOUSE_NATIVE_PORT", "9000")),
            user=os.getenv("CLICKHOUSE_USER", "default"),
            password=os.getenv("CLICKHOUSE_PASSWORD", "root")
        )
        client.execute("SELECT 1")
        logger.info("✅ Successfully connected to ClickHouse")
        break
    except Exception as e:
        logger.warning("ClickHouse not ready, retrying in 3s... %s", str(e))
        time.sleep(3)
else:
    raise Exception("❌ Failed to connect to ClickHouse after retries")

# ✅ Create table if not exists
client.execute('''
CREATE TABLE IF NOT EXISTS analytics (
    event_type String,
    page String,
    element String,
    scroll_depth Float32,
    duration Float32,
    session_id String,
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY timestamp
''')

# ✅ API endpoint to track events
@app.post("/track")
async def track_event(data: TrackEvent):
    try:
        logger.info(f"📩 Received data: {data}")

        client.execute(
            "INSERT INTO analytics (event_type, page, element, scroll_depth, duration, session_id, timestamp) VALUES",
            [[
                data.event_type,
                data.page,
                data.element,
                float(data.scroll_depth),
                float(data.duration),
                data.session_id,
                datetime.datetime.utcnow()
            ]]
        )

        logger.info("✅ Data inserted successfully!")
        return {"message": "Event tracked"}

    except Exception as e:
        logger.error("❌ Insert failed: %s", str(e))
        return {"error": str(e)}

