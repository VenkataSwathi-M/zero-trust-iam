# iam_core/api/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

router = APIRouter()

class DecisionBroadcaster:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for ws in list(self.connections):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(ws)

# ✅ MUST EXIST at module level
decision_broadcaster = DecisionBroadcaster()

@router.websocket("/ws/decisions")
async def decision_ws(websocket: WebSocket):
    await decision_broadcaster.connect(websocket)
    try:
        while True:
            await asyncio.sleep(10)  # ✅ keep alive
    except WebSocketDisconnect:
        decision_broadcaster.disconnect(websocket)