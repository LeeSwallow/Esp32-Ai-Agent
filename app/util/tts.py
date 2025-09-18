import json
import os
import uuid
import asyncio

import pyttsx3
from fastapi import WebSocket

from app.util.conn import get_ws, get_lock


tts_engine = pyttsx3.init()

# Persistent audio storage directory
AUDIO_DIR = os.path.join(".", "database", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


def synthesize_to_wav_file(text: str) -> str:
    filename = f"{uuid.uuid4().hex}.wav"
    path = os.path.join(AUDIO_DIR, filename)
    # pyttsx3는 블로킹이므로 별도 스레드에서 돌리거나 to_thread로 래핑해서 사용
    tts_engine.save_to_file(text, path)
    tts_engine.runAndWait()
    return path


async def stream_file_over_websocket(ws: WebSocket, file_path: str, chunk_size: int = 4096, content_type: str = "audio/wav") -> None:
    await ws.send_text(json.dumps({"type": "audio_start", "content_type": content_type}))
    try:
        with open(file_path, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                await ws.send_bytes(data)
    finally:
        await ws.send_text(json.dumps({"type": "audio_end"}))


async def speak_to_device_id(device_id: str, text: str) -> None:
    ws = get_ws(device_id)
    if ws is None:
        raise RuntimeError("Device not connected")

    lock = get_lock(device_id)
    async with lock:
        # 블로킹 합성은 스레드로 이동
        wav_path = await asyncio.to_thread(synthesize_to_wav_file, text)
        try:
            await stream_file_over_websocket(ws, wav_path)
        finally:
            try:
                os.remove(wav_path)
            except OSError:
                pass


async def stream_path_to_device_id(device_id: str, file_path: str, content_type: str = "audio/wav", cleanup: bool = True) -> None:
    ws = get_ws(device_id)
    if ws is None:
        raise RuntimeError("Device not connected")

    lock = get_lock(device_id)
    async with lock:
        try:
            await stream_file_over_websocket(ws, file_path, content_type=content_type)
        finally:
            if cleanup:
                try:
                    os.remove(file_path)
                except OSError:
                    pass


async def tts_and_stream_background(device_id: str, text: str) -> None:
    # Run blocking TTS synthesis in a thread, then stream
    wav_path = await asyncio.to_thread(synthesize_to_wav_file, text)
    await stream_path_to_device_id(device_id, wav_path, content_type="audio/wav", cleanup=True)


