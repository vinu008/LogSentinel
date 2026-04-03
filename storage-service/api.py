from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import db
import asyncio
import json

app = FastAPI(title="LogSentinel Query API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# keep track of connected dashboard clients
connected_clients: List[WebSocket] = []

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

@app.websocket("/ws/anomalies")
async def anomaly_ws(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(30)  # keep alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def broadcast_anomaly(anomaly: dict):
    """Call this from the anomaly engine to push to all dashboard clients."""
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(anomaly))
        except Exception:
            connected_clients.remove(client)
