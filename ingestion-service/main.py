from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import producer

app = FastAPI(title="LogSentinel Ingestion Service")


class LogEvent(BaseModel):
    timestamp: datetime
    service: str
    level: str
    message: str
    metadata: Optional[dict] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest(event: LogEvent):
    try:
        producer.publish(event.model_dump(mode="json"))
        return {"status": "accepted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/batch")
def ingest_batch(events: list[LogEvent]):
    try:
        for event in events:
            producer.publish(event.model_dump(mode="json"))
        return {"status": "accepted", "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
