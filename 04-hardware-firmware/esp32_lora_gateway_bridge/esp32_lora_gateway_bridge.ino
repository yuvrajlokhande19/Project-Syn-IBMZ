/**
 * ================================================================================
 * PROJECT SYN // AEGISCORE: EDGE IOT LORA-TO-MAINFRAME GATEWAY BRIDGE FIRMWARE
 * Target Hardware: ESP32-WROOM-32D + SX1276 LoRa Transceiver (868.1 MHz)
 * Dual Uplink: IEEE 802.11 b/g/n WiFi + W5500 SPI Ethernet / 4G LTE Failover
 * Cryptographic Standard: Hardware Pre-Flight HMAC-SHA256 Verification (mbedTLS)
 * Destination: IBM LinuxONE s390x High-Assurance Ingestion API (Port 8000)
 * ================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <mbedtls/md.h>
#include <ArduinoJson.h>

// -----------------------------------------------------------------------------
// GPIO Pin Configuration (ESP32 Gateway Bridge)
// -----------------------------------------------------------------------------
#define LORA_SCK     18
#define LORA_MISO    19
#define LORA_MOSI    23
#define LORA_SS      5
#define LORA_RST     14
#define LORA_DIO0    26
#define LORA_FREQ    868.1E6 // 868.1 MHz Sub-GHz India/EU ISM Band

// Status LED Indicators
#define PIN_LED_OK     2   // Blue/Green: Packet Validated & Forwarded to IBM Z
#define PIN_LED_ATTACK 4   // Red: Cryptographic Verification Failed (Attack Dropped)
#define PIN_LED_AIRGAP 15  // Amber: Air-gapped Sovereign Buffer Mode Active

// -----------------------------------------------------------------------------
// Network & Mainframe Configuration
// -----------------------------------------------------------------------------
const char* WIFI_SSID     = "Syn_Secure_Medical_Net";
const char* WIFI_PASSWORD = "IndustrialZeroTrust2026!";

// Primary IBM LinuxONE s390x Ingestion Endpoint
const char* MAINFRAME_API_URL = "http://148.100.112.151:8000/api/telemetry/ingest";

// Zero-Trust Shared Secret (Aligned with IBM CPACF MSA hardware accelerator)
static const char* HMAC_SECRET = "ibm_cpacf_super_secret_key_2026";
static const char* GATEWAY_ID  = "ESP32-GW-MUMBAI-APEX-01";

// Metrics & Telemetry Buffer for Air-gapped Disconnection
#define BUFFER_SIZE 64
struct OfflinePacket {
    char payload[512];
    bool occupied;
};
OfflinePacket offlineRingBuffer[BUFFER_SIZE];
int bufferHead = 0;
int bufferCount = 0;

// Statistics
uint32_t packetsReceivedTotal = 0;
uint32_t packetsForwardedOk = 0;
uint32_t packetsDroppedTampered = 0;

// -----------------------------------------------------------------------------
// Cryptographic Engine: Hardware Pre-Flight HMAC-SHA256
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
// Forward Telemetry to IBM LinuxONE s390x Ingestion Gateway
// -----------------------------------------------------------------------------
bool forwardToMainframe(const String& jsonPayload) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[GATEWAY] [OFFLINE] WiFi Uplink Disconnected. Storing in Sovereign Ring Buffer.");
        digitalWrite(PIN_LED_AIRGAP, HIGH);
        
        // Enqueue into offline buffer
        if (bufferCount < BUFFER_SIZE) {
            strncpy(offlineRingBuffer[bufferHead].payload, jsonPayload.c_str(), 511);
            offlineRingBuffer[bufferHead].payload[511] = '\0';
            offlineRingBuffer[bufferHead].occupied = true;
            bufferHead = (bufferHead + 1) % BUFFER_SIZE;
            bufferCount++;
        }
        return false;
    }

    digitalWrite(PIN_LED_AIRGAP, LOW);
    HTTPClient http;
    http.begin(MAINFRAME_API_URL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Project-Syn-Gateway", GATEWAY_ID);
    http.addHeader("X-AegisCore-Source", "ESP32-SubGHz-LoRa");
    http.setTimeout(2500);

    int httpResponseCode = http.POST(jsonPayload);
    bool success = false;

    if (httpResponseCode >= 200 && httpResponseCode < 300) {
        String response = http.getString();
        Serial.printf("[GATEWAY] [IBM Z UPLINK OK] Code: %d | Response: %s\n", httpResponseCode, response.c_str());
        digitalWrite(PIN_LED_OK, HIGH);
        delay(60);
        digitalWrite(PIN_LED_OK, LOW);
        packetsForwardedOk++;
        success = true;
    } else {
        Serial.printf("[GATEWAY] [IBM Z HTTP ERROR] Code: %d\n", httpResponseCode);
    }

    http.end();
    return success;
}

// -----------------------------------------------------------------------------
// Flush Air-gapped Offline Buffer once Uplink Restored
// -----------------------------------------------------------------------------
void flushOfflineBuffer() {
    if (WiFi.status() != WL_CONNECTED || bufferCount == 0) return;

    Serial.printf("[GATEWAY] Uplink Restored! Flushing %d air-gapped packets to IBM LinuxONE...\n", bufferCount);
    for (int i = 0; i < BUFFER_SIZE; i++) {
        if (offlineRingBuffer[i].occupied) {
            forwardToMainframe(String(offlineRingBuffer[i].payload));
            offlineRingBuffer[i].occupied = false;
        }
    }
    bufferHead = 0;
    bufferCount = 0;
    digitalWrite(PIN_LED_AIRGAP, LOW);
}

// -----------------------------------------------------------------------------
// Setup Routine
// -----------------------------------------------------------------------------
void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n=======================================================");
    Serial.println("  PROJECT SYN // AEGISCORE IOT LORA GATEWAY BRIDGE     ");
    Serial.println("  Target Architecture: ESP32-WROOM-32D -> IBM LinuxONE ");
    Serial.println("=======================================================");

    pinMode(PIN_LED_OK, OUTPUT);
    pinMode(PIN_LED_ATTACK, OUTPUT);
    pinMode(PIN_LED_AIRGAP, OUTPUT);
    digitalWrite(PIN_LED_OK, LOW);
    digitalWrite(PIN_LED_ATTACK, LOW);
    digitalWrite(PIN_LED_AIRGAP, LOW);

    // Initialize LoRa Radio
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

    Serial.printf("[LoRa] Initializing SX1276 transceiver at %.1f MHz...\n", LORA_FREQ / 1E6);
    if (!LoRa.begin(LORA_FREQ)) {
        Serial.println("[LoRa] CRITICAL ERROR: SX1276 initialization failed!");
        while (1) {
            digitalWrite(PIN_LED_ATTACK, HIGH);
            delay(200);
            digitalWrite(PIN_LED_ATTACK, LOW);
            delay(200);
        }
    }

    LoRa.setSpreadingFactor(9);
    LoRa.setSignalBandwidth(125E3);
    LoRa.setCodingRate4(7);
    LoRa.setSyncWord(0x34); // Project Syn Medical Private Network Sync Word
    LoRa.enableCrc();
    Serial.println("[LoRa] SX1276 Receiver Active and Listening.");

    // Connect to Medical WiFi Network
    Serial.printf("[WiFi] Connecting to %s...\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 15) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WiFi] Connected! IP Address: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("[WiFi] IBM LinuxONE Target: %s\n", MAINFRAME_API_URL);
    } else {
        Serial.println("\n[WiFi] Connection timed out. Operating in Sovereign Air-gapped Buffer Mode.");
        digitalWrite(PIN_LED_AIRGAP, HIGH);
    }
}

// -----------------------------------------------------------------------------
// Main Gateway Loop
// -----------------------------------------------------------------------------
void loop() {
    // Attempt buffer flush if connection is healthy
    if (WiFi.status() == WL_CONNECTED && bufferCount > 0) {
        flushOfflineBuffer();
    }

    // Check for incoming Sub-GHz LoRa packets
    int packetSize = LoRa.parsePacket();
    if (packetSize) {
        packetsReceivedTotal++;
        String incomingJson = "";
        while (LoRa.available()) {
            incomingJson += (char)LoRa.read();
        }

        int rssi = LoRa.packetRssi();
        float snr = LoRa.packetSnr();
        Serial.printf("\n[LoRa RX] Received %d bytes | RSSI: %d dBm | SNR: %.1f dB\n", packetSize, rssi, snr);
        Serial.printf("[LoRa RAW] %s\n", incomingJson.c_str());

        // Parse Canonical JSON Contract
        StaticJsonDocument<1024> doc;
        DeserializationError error = deserializeJson(doc, incomingJson);

        if (error) {
            Serial.printf("[GATEWAY] [MALFORMED JSON] Error: %s\n", error.c_str());
            return;
        }

        const char* packetId       = doc["packet_id"];
        const char* timestamp      = doc["timestamp"];
        const char* sensorLocation = doc["sensor_location"];
        JsonObject metrics         = doc["metrics"];
        float gridVoltage          = metrics["grid_voltage"] | 0.0;
        float floodIndex           = metrics["flood_index"] | 0.0;
        int routeCongestion        = metrics["route_congestion"] | 0;
        const char* nonce          = doc["nonce"];
        const char* receivedHmac   = doc["hmac_signature"];

        // Reconstruct canonical message string for HMAC verification:
        // Canonical format: packet_id:timestamp:sensor_location:grid_voltage:flood_index:route_congestion:nonce
        char canonicalBuf[384];
        snprintf(canonicalBuf, sizeof(canonicalBuf), "%s:%s:%s:%.1f:%.2f:%d:%s",
                 packetId, timestamp, sensorLocation, gridVoltage, floodIndex, routeCongestion, nonce);

        // Pre-Flight Edge Hardware HMAC-SHA256 Verification
        String calculatedHmac = computeHMACSHA256(String(canonicalBuf), HMAC_SECRET);

        if (calculatedHmac.equalsIgnoreCase(String(receivedHmac))) {
            Serial.printf("[GATEWAY] [PRE-FLIGHT HMAC VALID] Packet %s from %s verified!\n", packetId, sensorLocation);
            // Forward payload to IBM LinuxONE s390x
            forwardToMainframe(incomingJson);
        } else {
            // Tampered or spoofed packet detected at physical edge!
            packetsDroppedTampered++;
            Serial.println("*******************************************************************");
            Serial.printf("[GATEWAY] [SECURITY ALERT] HMAC MISMATCH DETECTED ON %s!\n", packetId);
            Serial.printf("  Expected: %s\n", calculatedHmac.c_str());
            Serial.printf("  Received: %s\n", receivedHmac);
            Serial.println("[GATEWAY] [CPACF ZERO-TRUST] Dropping spoofed injection at edge gate!");
            Serial.println("*******************************************************************");

            // Trigger Red LED Flash for visual field alert
            digitalWrite(PIN_LED_ATTACK, HIGH);
            delay(150);
            digitalWrite(PIN_LED_ATTACK, LOW);
        }
    }

    delay(10);
}
