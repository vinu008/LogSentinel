from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="LogSentinel Ingestion Service")


class LogEvent(BaseModel):
    timestamp: datetime
    service: str
    level: str  # DEBUG, INFO, WARN, ERROR, FATAL
    message: str
    metadata: Optional[dict] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(event: LogEvent):
    # TODO: publish to Kafka
    return {"status": "accepted"}


@app.post("/ingest/batch")
def ingest_batch(events: list[LogEvent]):
    # TODO: publish batch to Kafka
    return {"status": "accepted", "count": len(events)}
