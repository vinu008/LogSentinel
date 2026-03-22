from fastapi import FastAPI
from typing import Optional
import db

app = FastAPI(title="LogSentinel Query API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/logs")
def get_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100
):
    db.init_db()
    results = db.query_logs(service=service, level=level, limit=limit)
    return {"logs": results, "count": len(results)}
