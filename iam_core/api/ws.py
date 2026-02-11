from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

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
        for ws in list(self.connections):
            await ws.send_json(message)

# 🔥 THIS MUST EXIST AT MODULE LEVEL
decision_broadcaster = DecisionBroadcaster()


@router.websocket("/ws/decisions")
async def decision_ws(websocket: WebSocket):
    await decision_broadcaster.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        decision_broadcaster.disconnect(websocket)