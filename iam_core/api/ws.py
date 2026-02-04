from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from services.decision_ws import decision_broadcaster

router = APIRouter()

@router.websocket("/ws/decisions")
async def decision_ws(websocket: WebSocket):
    await decision_broadcaster.connect(websocket)

    try:
        while True:
            await asyncio.sleep(30)  # keep alive
    except WebSocketDisconnect:
        decision_broadcaster.disconnect(websocket)