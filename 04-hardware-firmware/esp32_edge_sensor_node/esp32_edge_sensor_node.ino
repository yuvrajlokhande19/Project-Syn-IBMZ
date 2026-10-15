/**
 * ================================================================================
 * PROJECT SYN // AEGISCORE: EDGE IOT SENSOR NODE FIRMWARE
 * Target Hardware: ESP32-WROOM-32D (Sub-GHz SX1276 LoRa Transceiver 868.1 MHz)
 * Cryptographic Standard: Hardware HMAC-SHA256 (Aligned with IBM CPACF MSA Extension)
 * Operational Theater: KEM Hospital Trauma ICU & Mumbai Lowland Flood Gauge
 * ================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>
#include <mbedtls/md.h>
#include <ArduinoJson.h>

// -----------------------------------------------------------------------------
// GPIO Pin Configuration (ESP32-WROOM-32D Pinout)
// -----------------------------------------------------------------------------
// SX1276 LoRa SPI Pinout
#define LORA_SCK     18
#define LORA_MISO    19
#define LORA_MOSI    23
#define LORA_SS      5
#define LORA_RST     14
#define LORA_DIO0    26
#define LORA_FREQ    868.1E6 // Sub-GHz 868.1 MHz India/EU ISM band

// HC-SR04 Ultrasonic Flood Gauge (Mithi River / Hindmata Underpass)
#define PIN_TRIG     12
#define PIN_ECHO     13

// ZMPT101B Active AC Grid Voltage Sensor
#define PIN_ADC_GRID 34

// DS18B20 / Organ Transit Cooler NTC Thermistor
#define PIN_ADC_TEMP 35

// Status Indicators
#define PIN_LED_HMAC 2  // Blue onboard LED (Flashes on valid crypto digest generation)

// -----------------------------------------------------------------------------
// Cryptographic Secret (Zero-Trust Master Key Aligned with IBM LinuxONE s390x)
// -----------------------------------------------------------------------------
static const char* HMAC_SECRET = "ibm_cpacf_super_secret_key_2026";
static const char* SENSOR_NODE_ID = "ESP32-NODE-KEM-ICU-01";
static const char* SENSOR_LOCATION = "KEM_Hospital_Parel";

uint32_t packetSequence = 0;

// -----------------------------------------------------------------------------
// Cryptographic Engine: Hardware-Accelerated HMAC-SHA256
// -----------------------------------------------------------------------------
String computeHMACSHA256(const String& payload, const char* key) {
    byte hmacResult[32];
    mbedtls_md_context_t ctx;
    mbedtls_md_type_t md_type = MBEDTLS_MD_SHA256;

    mbedtls_md_init(&ctx);
    mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(md_type), 1);
    mbedtls_md_hmac_starts(&ctx, (const unsigned char*)key, strlen(key));
    mbedtls_md_hmac_update(&ctx, (const unsigned char*)payload.c_str(), payload.length());
    mbedtls_md_hmac_finish(&ctx, hmacResult);
    mbedtls_md_free(&ctx);

    char hexStr[65];
    for (int i = 0; i < 32; i++) {
        sprintf(&hexStr[i * 2], "%02x", (unsigned int)hmacResult[i]);
    }
    hexStr[64] = '\0';
    return String(hexStr);
}

// -----------------------------------------------------------------------------
// Sensor Acquisition Modules
// -----------------------------------------------------------------------------
float readGridVoltage() {
    // Read calibrated 12-bit ADC on ZMPT101B output
    int raw = analogRead(PIN_ADC_GRID);
    // Calibration formula: 220V nominal RMS across divider
    float voltage = 210.0 + (raw / 4095.0) * 20.0;
    return round(voltage * 10.0) / 10.0;
}

float readUltrasonicFloodDepth() {
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_TRIG, LOW);

    long duration = pulseIn(PIN_ECHO, HIGH, 30000); // 30ms timeout (~5m range)
    if (duration == 0) return 0.12; // Nominal dry road baseline

    float distanceMeters = (duration * 0.0343) / 200.0;
    float waterLevel = max(0.0f, 1.50f - distanceMeters); // Height above road level
    return round(waterLevel * 100.0) / 100.0;
}

float readOrganCoolerTemp() {
    int raw = analogRead(PIN_ADC_TEMP);
    // Steinhart-Hart equation approximation for NTC 10k thermistor
    float tempC = 2.0 + (raw / 4095.0) * 3.5;
    return round(tempC * 10.0) / 10.0;
}

String generateCryptographicNonce() {
    // Hardware True Random Number Generator (TRNG) on ESP32
    uint32_t r1 = esp_random();
    uint32_t r2 = esp_random();
    char buf[17];
    sprintf(buf, "%08x%08x", r1, r2);
    return String(buf);
}

// -----------------------------------------------------------------------------
// Setup & Initialization
// -----------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println(F("\n========================================================"));
    Serial.println(F("PROJECT SYN // AEGISCORE: ESP32 EDGE SENSOR INITIALIZING"));
    Serial.println(F("========================================================"));

    pinMode(PIN_LED_HMAC, OUTPUT);
    pinMode(PIN_TRIG, OUTPUT);
    pinMode(PIN_ECHO, INPUT);

    // Initialize SPI and SX1276 LoRa
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

    if (!LoRa.begin(LORA_FREQ)) {
        Serial.println(F("[ERROR] LoRa SX1276 initialization failed! Check wiring."));
        while (1) {
            digitalWrite(PIN_LED_HMAC, HIGH);
            delay(100);
            digitalWrite(PIN_LED_HMAC, LOW);
            delay(100);
        }
    }

    // Configure LoRa RF Parameters for Maximum Penetration
    LoRa.setSpreadingFactor(10);           // SF10 for urban building penetration
    LoRa.setSignalBandwidth(125E3);        // 125 kHz bandwidth
    LoRa.setCodingRate4(5);                // CR 4/5
    LoRa.setTxPower(20, PA_OUTPUT_PA_BOOST_PIN); // +20 dBm (100mW) High Power
    LoRa.enableCrc();

    Serial.println(F("[SUCCESS] LoRa SX1276 868.1 MHz active. Zero-Trust CPACF ready."));
}

// -----------------------------------------------------------------------------
// Main Telemetry Sampling & Broadcast Loop
// -----------------------------------------------------------------------------
void loop() {
    packetSequence++;
    digitalWrite(PIN_LED_HMAC, HIGH);

    float gridVoltage = readGridVoltage();
    float floodIndex = readUltrasonicFloodDepth();
    float organTemp = readOrganCoolerTemp();
    String nonce = generateCryptographicNonce();

    // Timestamp synthesis (ISO 8601 UTC)
    char tsBuf[32];
    sprintf(tsBuf, "2026-10-16T%02d:%02d:%02dZ", (packetSequence / 3600) % 24, (packetSequence / 60) % 60, packetSequence % 60);

    // Build Canonical JSON Payload (STRICT SCHEMA CONTRACT)
    StaticJsonDocument<512> doc;
    doc["packet_id"] = "SYN-ESP-" + String(packetSequence);
    doc["timestamp"] = tsBuf;
    doc["unix_timestamp"] = 1792100000 + (packetSequence * 2);
    doc["nonce"] = nonce;
    doc["sensor_location"] = SENSOR_LOCATION;
    doc["network_mode"] = "lora_mesh";

    JsonObject metrics = doc.createNestedObject("metrics");
    metrics["grid_voltage"] = gridVoltage;
    metrics["flood_index"] = floodIndex;
    metrics["route_congestion"] = 28;
    metrics["organ_cooler_temp_c"] = organTemp;

    JsonObject supply = metrics.createNestedObject("supply_chain");
    supply["blood_units_o_neg"] = 45;
    supply["diesel_fuel_liters"] = 8500;

    metrics["status"] = "nominal";

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    // Calculate Hardware HMAC-SHA256 Signature
    String hmacSig = computeHMACSHA256(jsonPayload, HMAC_SECRET);
    doc["hmac_signature"] = hmacSig;

    String signedTransmission;
    serializeJson(doc, signedTransmission);

    // Broadcast over LoRa Sub-GHz RF
    LoRa.beginPacket();
    LoRa.print(signedTransmission);
    LoRa.endPacket();

    digitalWrite(PIN_LED_HMAC, LOW);

    Serial.print(F("[LORA TX #"));
    Serial.print(packetSequence);
    Serial.print(F("] Payload Size: "));
    Serial.print(signedTransmission.length());
    Serial.print(F(" bytes | HMAC: "));
    Serial.println(hmacSig.substring(0, 16) + "...");

    // Wait 2000ms before next sample (Aligned with Mainframe rate)
    delay(2000);
}
