# iam_core/api/ws_banking.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json

router = APIRouter(prefix="/ws", tags=["WebSocket"])

class Broadcaster:
    def __init__(self):
        self.clients: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.clients.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.clients:
            self.clients.remove(ws)

    async def broadcast(self, payload: Dict[str, Any]):
        msg = json.dumps(payload)
        for ws in list(self.clients):
            try:
                await ws.send_text(msg)
            except Exception:
                self.disconnect(ws)

banking_broadcaster = Broadcaster()

@router.websocket("/banking")
async def ws_banking(ws: WebSocket):
    await banking_broadcaster.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        banking_broadcaster.disconnect(ws)