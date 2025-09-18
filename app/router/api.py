from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud import device as device_crud
from app.scheme.device import DeviceCreate, DeviceResponse, SpeakRequest
from app.util.db import get_db
from app.util.conn import get_connected_ids
from app.util.tts import speak_to_device_id, stream_path_to_device_id
from app.util.conn import get_ws, get_lock


router = APIRouter(prefix="")


@router.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "connected_ids": get_connected_ids()})


@router.get("/devices", response_model=List[DeviceResponse])
def list_devices(db: Session = Depends(get_db)):
    return device_crud.list_all(db)


@router.post("/devices", response_model=DeviceResponse)
def register_device(payload: DeviceCreate, db: Session  = Depends(get_db)):
    found = device_crud.get_by_name(db, payload.device_id)
    if found:
        return found
    return device_crud.create(db, payload.device_id)


@router.post("/devices/{device_id}/speak")
async def speak_device(device_id: str, req: SpeakRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="text is required")
    import asyncio
    asyncio.create_task(speak_to_device_id(device_id, req.text))
    return JSONResponse({"status": "queued", "device_id": device_id})


@router.post("/devices/{device_id}/upload-wav")
async def upload_wav_and_stream(device_id: str, file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail=".wav file required")

    ws = get_ws(device_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="Device not connected")

    # Save temp WAV with UUID filename and stream in background
    import os, uuid
    filename = f"{uuid.uuid4().hex}.wav"
    base_dir = os.path.join(".", "database", "audio")
    os.makedirs(base_dir, exist_ok=True)
    wav_path = os.path.join(base_dir, filename)

    content = await file.read()
    with open(wav_path, "wb") as f:
        f.write(content)

    import asyncio
    asyncio.create_task(stream_path_to_device_id(device_id, wav_path, content_type="audio/wav", cleanup=True))

    return JSONResponse({"status": "queued", "device_id": device_id})


