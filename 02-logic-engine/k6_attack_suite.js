/**
 * ============================================================================
 * Project Syn / AegisCore: High-Throughput Burst & Shock-Absorber Load Suite
 * Target: IBM LinuxONE s390x Mainframe Ingestion Gate (1,000+ req/sec Burst)
 * ============================================================================
 * Tests the asynchronous shock-absorber queue and CPACF cryptographic gateway
 * under extreme load, combining nominal traffic with mixed cyber attack vectors.
 * ============================================================================
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import crypto from 'k6/crypto';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom Metrics
const validIngestRate = new Rate('rate_valid_ingest');
const attackBlockedRate = new Rate('rate_attack_blocked');
const queueLatencyTrend = new Trend('crypto_gate_duration');

const BASE_URL = __ENV.MAINFRAME_URL || 'http://127.0.0.1:8000/api/telemetry/ingest';
const SECRET_KEY = __ENV.MAINFRAME_SECRET_KEY || 'fallback_secret_key';

const LOCATIONS = [
  'GMC_Nagpur',
  'Mayo_Hospital',
  'AIIMS_Nagpur',
  'Lata_Mangeshkar_Hospital',
  'Wockhardt_Hospital'
];

export const options = {
  scenarios: {
    shock_absorber_burst: {
      executor: 'ramping-arrival-rate',
      startRate: 250,
      timeUnit: '1s',
      preAllocatedVUs: 200,
      maxVUs: 600,
      stages: [
        { target: 500, duration: '10s' },    // Warm-up ramp
        { target: 1200, duration: '25s' },   // Burst peak (> 1,000 req/sec)
        { target: 200, duration: '10s' },    // Scale down
      ],
    },
  },
  thresholds: {
    // 95% of requests must complete under 200ms
    http_req_duration: ['p(95)<200', 'p(99)<400'],
    // Valid ingest requests must succeed
    rate_valid_ingest: ['rate>0.98'],
    // All cyber attacks must be intercepted with 401/403
    rate_attack_blocked: ['rate>0.98'],
  },
};

function generateRandomHex(bytes) {
  const arr = new Uint8Array(bytes);
  for (let i = 0; i < bytes; i++) {
    arr[i] = Math.floor(Math.random() * 256);
  }
  return Array.from(arr, b => b.toString(16).padStart(2, '0')).join('');
}

export default function () {
  const randVal = Math.random();
  const now = Date.now() / 1000;
  const location = LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)];

  let isAttack = false;
  let attackType = 'none';
  let expectedStatus = 200;

  let packet = {
    packet_id: `K6-${__VU}-${__ITER}-${Math.floor(Math.random() * 100000)}`,
    timestamp: new Date().toISOString(),
    unix_timestamp: now,
    nonce: generateRandomHex(8),
    sensor_location: location,
    network_mode: 'satellite_api',
    metrics: {
      grid_voltage: 220.0 + (Math.random() * 4 - 2),
      flood_index: Math.min(0.3, Math.max(0.0, Math.random() * 0.2)),
      route_congestion: Math.floor(Math.random() * 50 + 20),
      temperature: 33.0,
      windspeed: 12.0,
      supply_chain: {
        blood_units_o_neg: 60,
        diesel_fuel_liters: 2200
      },
      cctv_intel: {
        status: 'CLEAR',
        confidence: 0.98
      }
    },
    status: 'nominal'
  };

  // Determine attack vector (20% adversarial traffic, 80% nominal burst)
  if (randVal < 0.05) {
    // Vector 1: Tampered Signature
    isAttack = true;
    attackType = 'tamper';
    expectedStatus = 401;
  } else if (randVal < 0.10) {
    // Vector 2: Replay Nonce
    isAttack = true;
    attackType = 'replay';
    expectedStatus = 401;
    packet.nonce = 'constant_replayed_nonce_k6';
  } else if (randVal < 0.15) {
    // Vector 3: Stale Timestamp (120s past)
    isAttack = true;
    attackType = 'stale';
    expectedStatus = 401;
    packet.unix_timestamp = now - 120.0;
  } else if (randVal < 0.20) {
    // Vector 4: Spoofed Physics (Severe flood, full voltage, zero congestion)
    isAttack = true;
    attackType = 'spoof';
    expectedStatus = 403;
    packet.metrics.flood_index = 0.95;
    packet.metrics.grid_voltage = 230.0;
    packet.metrics.route_congestion = 5;
  }

  const payloadString = JSON.stringify(packet);

  // Compute HMAC-SHA256 signature
  let signature;
  if (attackType === 'tamper') {
    // Deliberately corrupted signature
    signature = 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef';
  } else {
    signature = crypto.hmac('sha256', SECRET_KEY, payloadString, 'hex');
  }

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-Signature': signature,
    },
    tags: {
      attack_type: attackType,
    },
  };

  const startTime = Date.now();
  const response = http.post(BASE_URL, payloadString, params);
  queueLatencyTrend.add(Date.now() - startTime);

  if (!isAttack) {
    const success = check(response, {
      'valid packet accepted (200)': (r) => r.status === 200,
    });
    validIngestRate.add(success);
  } else {
    const blocked = check(response, {
      'attack correctly blocked (401 or 403)': (r) => r.status === expectedStatus,
    });
    attackBlockedRate.add(blocked);
  }
}
