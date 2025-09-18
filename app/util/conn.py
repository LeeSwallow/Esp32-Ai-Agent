import asyncio
from typing import Dict, List, Optional

from fastapi import WebSocket


# DB id -> websocket / lock / ip
_id_to_ws: Dict[str, WebSocket] = {}
_id_to_lock: Dict[str, asyncio.Lock] = {}


def get_connected_ids() -> List[str]:
    return list(_id_to_ws.keys())


def get_ws(device_id: str) -> Optional[WebSocket]:
    return _id_to_ws.get(device_id)

def get_lock(device_id: str) -> asyncio.Lock:
    if device_id not in _id_to_lock:
        _id_to_lock[device_id] = asyncio.Lock()
    return _id_to_lock[device_id]

def register_connection(device_id: str, ws: WebSocket) -> None:
    if device_id in _id_to_ws:
        _id_to_ws[device_id] = ws
    _id_to_lock[device_id] = asyncio.Lock()


def unregister_connection(device_id: str) -> None:
    _id_to_ws.pop(device_id, None)
    _id_to_lock.pop(device_id, None)
