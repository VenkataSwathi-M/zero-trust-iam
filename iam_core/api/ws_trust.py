from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter(tags=["Trust WS"])

# sid -> set(websocket)
CLIENTS = {}

async def broadcast_trust(sid: str, payload: dict):
    conns = CLIENTS.get(sid) or set()
    dead = []
    for ws in list(conns):
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            dead.append(ws)
    for ws in dead:
        conns.discard(ws)

@router.websocket("/ws/trust/{sid}")
async def ws_trust(websocket: WebSocket, sid: str):
    await websocket.accept()
    CLIENTS.setdefault(sid, set()).add(websocket)

    # send a hello so UI knows connected
    await websocket.send_text(json.dumps({"type": "TRUST_WS_CONNECTED", "sid": sid}))

    try:
        while True:
            # keep connection alive (client can send ping)
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        CLIENTS.get(sid, set()).discard(websocket)