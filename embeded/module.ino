#include <WiFi.h>
#include <WiFiManager.h>
#include <ArduinoWebsockets.h>

using namespace websockets;

const char* SERVER_HOST = "192.168.0.10";   // 서버 IP
const int   SERVER_PORT = 8000;              // 서버 포트
const char* DEVICE_ID   = "esp32-1";        // 고유 디바이스 ID(출하/초기화 시 설정)

// 매직 넘버 상수화
const unsigned long RECONNECT_INTERVAL_MS = 5000;
const int WIFI_PORTAL_TIMEOUT_SEC = 180;

WebsocketsClient wsClient;
unsigned long lastReconnectAttemptMs = 0;

bool connectWiFiManager() {
    WiFi.mode(WIFI_STA);
    WiFiManager wm;
    wm.setTitle("ESP32 WiFi Setup");
    wm.setConfigPortalBlocking(true);
    wm.setConfigPortalTimeout(WIFI_PORTAL_TIMEOUT_SEC); // 3분 후 자동 종료

    Serial.println("Trying autoConnect() or opening portal 'ESP32-Setup'...");
    bool res = wm.autoConnect("ESP32-Setup");
    if (!res) {
        Serial.println("WiFiManager failed to connect");
        return false;
    }
    Serial.print("WiFi connected, IP: ");
    Serial.println(WiFi.localIP());
    return true;
}

bool connectWebSocket() {
    String url = String("ws://") + SERVER_HOST + ":" + String(SERVER_PORT) + "/ws/device/" + DEVICE_ID;
    Serial.print("Connecting WS: ");
    Serial.println(url);

    bool ok = wsClient.connect(url);
    if (!ok) {
        Serial.println("WS connect failed");
        return false;
    }

    wsClient.onMessage([](WebsocketsMessage message) {
        if (message.isBinary()) {
            // 단순히 수신 바이트 수 출력 (MVP)
            size_t len = message.length();
            Serial.print("[BIN] bytes: ");
            Serial.println(len);
        } else {
            Serial.print("[TXT] ");
            Serial.println(message.data());
        }
    });

    wsClient.onEvent([](WebsocketsEvent event, String data) {
        if (event == WebsocketsEvent::ConnectionOpened) {
            Serial.println("WS opened");
        } else if (event == WebsocketsEvent::ConnectionClosed) {
            Serial.println("WS closed");
        } else if (event == WebsocketsEvent::GotPing) {
            Serial.println("WS ping");
        } else if (event == WebsocketsEvent::GotPong) {
            Serial.println("WS pong");
        }
    });

    return true;
}

void setup() {
    Serial.begin(115200);
    delay(500);
    if (!connectWiFiManager()) {
        delay(3000);
        ESP.restart();
    }
    connectWebSocket();
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        // WiFi 재설정 포털 재시도
        if (!connectWiFiManager()) {
            delay(5000);
        }
        lastReconnectAttemptMs = millis();
    }

    if (!wsClient.available()) {
        unsigned long now = millis();
        if (now - lastReconnectAttemptMs >= RECONNECT_INTERVAL_MS) {
            lastReconnectAttemptMs = now;
            connectWebSocket();
        }
        delay(1);
        return;
    }

    wsClient.poll();
    delay(1);
}


