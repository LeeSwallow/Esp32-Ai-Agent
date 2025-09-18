## tts-arduino-server

FastAPI 기반 ESP32 TTS 스트리밍 MVP 서버.

### 실행

1) 설치

```bash
pip install -e .
```

2) 서버 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 엔드포인트

- `GET /health`: 상태 확인
- `GET /devices`: 현재 연결된 디바이스 ID 목록
- `WEBSOCKET /ws/device/{device_id}`: ESP32가 접속하는 소켓 (서버→디바이스 오디오 스트리밍)
- `POST /devices/{device_id}/speak`: 특정 디바이스로 TTS 오디오 스트리밍
  - body: `{ "text": "안녕하세요" }`

### 사용 예시

ESP32가 `ws://SERVER_IP:8000/ws/device/esp32-1`로 연결 중일 때:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"안녕하세요, 디바이스"}' \
  http://SERVER_IP:8000/devices/esp32-1/speak
```

### ESP32 스케치 개요

`embeded/module.ino` 예제는 WiFi 연결 후 웹소켓에 접속하여 서버 메시지를 수신합니다.
바이너리(오디오) 수신 시 바이트 수를 시리얼로 출력합니다.

