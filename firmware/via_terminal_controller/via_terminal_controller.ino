#include <Arduino.h>
#include <NimBLEDevice.h>

// VIA Terminal Hardware Controller
// ESP32 -> MOSFET -> 12V COB LED. Do NOT drive the COB directly from ESP32.

static const char* DEVICE_NAME = "VIA-HW";
static NimBLEUUID SERVICE_UUID("7c8d0001-4d2b-4c1f-9c0a-0d7b2c6e1001");
static NimBLEUUID STATE_UUID  ("7c8d0002-4d2b-4c1f-9c0a-0d7b2c6e1001");

constexpr uint8_t LED_PIN = 18;
constexpr uint32_t PWM_FREQ = 18000;
constexpr uint8_t PWM_RES = 12;
constexpr uint16_t PWM_MAX = (1 << PWM_RES) - 1;

String state = "idle";
uint32_t stateStarted = 0;

uint16_t pct(float p) {
  p = constrain(p, 0.0f, 1.0f);
  return (uint16_t)(p * PWM_MAX);
}

void setBrightness(float value) {
  ledcWrite(LED_PIN, pct(value));
}

float easeInOut(float t) {
  return t < 0.5f ? 2.0f*t*t : 1.0f - pow(-2.0f*t + 2.0f, 2.0f)/2.0f;
}

class StateCallbacks : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic* c, NimBLEConnInfo& info) override {
    std::string raw = c->getValue();
    if (raw.empty()) return;
    state = String(raw.c_str());
    state.toLowerCase();
    stateStarted = millis();
  }
};

void animateLed() {
  const uint32_t dt = millis() - stateStarted;
  if (state == "off") { setBrightness(0.0f); return; }
  if (state == "idle") {
    float t = min(dt / 800.0f, 1.0f);
    setBrightness(0.25f * easeInOut(t));
    return;
  }
  if (state == "active") {
    float t = min(dt / 450.0f, 1.0f);
    setBrightness(0.25f + (0.52f - 0.25f) * easeInOut(t));
    return;
  }
  if (state == "scan") {
    float phase = (millis() % 2200) / 2200.0f;
    float wave = 0.5f - 0.5f*cosf(phase * 2.0f * PI);
    setBrightness(0.54f + 0.14f * wave);
    return;
  }
  if (state == "success") {
    if (dt < 160) setBrightness(1.0f);
    else if (dt < 520) setBrightness(0.58f);
    else { state = "idle"; stateStarted = millis(); }
    return;
  }
  if (state == "error") {
    const uint32_t p = dt % 700;
    setBrightness((p < 100 || (p >= 220 && p < 320)) ? 0.92f : 0.24f);
    if (dt > 900) { state = "idle"; stateStarted = millis(); }
    return;
  }
  setBrightness(0.25f);
}

void setup() {
  Serial.begin(115200);
  ledcAttach(LED_PIN, PWM_FREQ, PWM_RES);
  setBrightness(0.0f);

  NimBLEDevice::init(DEVICE_NAME);
  NimBLEDevice::setPower(ESP_PWR_LVL_P6);
  NimBLEServer* server = NimBLEDevice::createServer();
  NimBLEService* service = server->createService(SERVICE_UUID);
  NimBLECharacteristic* stateCharacteristic = service->createCharacteristic(
    STATE_UUID,
    NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::READ
  );
  stateCharacteristic->setValue("idle");
  stateCharacteristic->setCallbacks(new StateCallbacks());
  service->start();

  NimBLEAdvertising* advertising = NimBLEDevice::getAdvertising();
  advertising->addServiceUUID(SERVICE_UUID);
  advertising->setName(DEVICE_NAME);
  advertising->enableScanResponse(true);
  advertising->start();
  stateStarted = millis();
}

void loop() {
  animateLed();
  delay(8);
}
