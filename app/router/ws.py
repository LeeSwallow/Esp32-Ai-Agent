import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.util.conn import register_connection, unregister_connection
from app.util.db import SessionLocal
from app.crud import device as device_crud


router = APIRouter()


@router.websocket("/ws/device/{device_id}")
async def device_ws(websocket: WebSocket, device_id: str) -> None:
    await websocket.accept()
    db = SessionLocal()
    try:
        device = device_crud.get_by_device_id(db, device_id)
        if not device:
            device = device_crud.create(db, device_id)
    finally:
        db.close()
    try:
        register_connection(device_id, websocket)
        await websocket.send_text(
            json.dumps({"type": "hello", "device_id": device_id})
        )
        while True:
            try:
                _ = await websocket.receive_text()
            except Exception:
                _ = await websocket.receive_bytes()
    except WebSocketDisconnect:
        pass
    finally:
        try:
            unregister_connection(device_id)
        except Exception:
            pass


