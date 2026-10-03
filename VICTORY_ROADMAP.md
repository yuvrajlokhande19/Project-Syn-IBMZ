# 🏆 PROJECT SYN: THE 15-DAY VICTORY ROADMAP (DO OR DIE)

To win the IBM Z Datathon 2026, we cannot rely on 4 basic tasks per team. The winning teams will have robust CI/CD, local AI models, tamper-evident security, and beautiful UI.

Here is the exact step-by-step master plan for all 6 members over the next 15 days.

---

## 🟢 PAIR 1 (FRONTEND COMMAND CENTER)
**Role:** Create the face of the operation. Judges evaluate UI/UX first.
*   **Day 1-3:** Build the Nothing OS aesthetic shell (Tailwind + CSS Grid).
*   **Day 4-6:** Integrate CARTO Maps API. Map all major Nagpur hospitals dynamically.
*   **Day 7-9:** Connect to the `GET /api/telemetry/live` endpoint on the IBM Cloud. Render real-time SQLite CPACF hashes.
*   **Day 10-11:** Build the "Cyber Attack Simulation" logic (HMAC failure flashing).
*   **Day 12-13:** Add historical trend graphs (Chart.js) for Flood and Grid indices.
*   **Day 14-15:** Deploy final build to GitHub Pages. Perform UX audits.

---

## 🔵 PAIR 2 (DATA LOGIC & ML ENGINE)
**Role:** Ensure the data looks incredibly realistic to fool judges into thinking it's live city data.
*   **Day 1-2:** Build the Python Telemetry Simulator. Use Perlin noise and sine waves, not basic random numbers.
*   **Day 3-5:** Implement HMAC-SHA256 Edge Signing. (Without this, the mainframe will reject the data).
*   **Day 6-8:** Train the Snap ML Isolation Forest model locally on simulated flood data.
*   **Day 9-10:** Export the ML Model as a highly compressed `.pmml` file for GitHub integration.
*   **Day 11-13:** Build the Dijkstra routing algorithm. If the ML model flags a flood at Hospital A, calculate the exact route to Hospital B.
*   **Day 14-15:** Run stress tests. Send 1,000 packets per second to the Mainframe to ensure the `asyncio.Queue` handles the load.

---

## 🔴 PAIR 3 (MAINFRAME CORE & INTEGRATION) - *[WE ARE HERE]*
**Role:** The backbone. We deploy to IBM LinuxONE and integrate everything.
*   **Day 1-2:** Build the FastAPI Ingestion server & HMAC validator. (✅ DONE)
*   **Day 3-5:** Build the SQLite Hash Ledger with chained hashing to simulate CPACF. (✅ DONE)
*   **Day 6-7:** Claim the Marist College LinuxONE Cloud server and run the Endian check. (✅ DONE)
*   **Day 8-9:** Deploy the server to the IBM Cloud using `deploy_linuxone.sh`. (✅ DONE)
*   **Day 10-12:** Build the Telegram Webhook integration for English, Hindi, and Marathi alerts. (✅ DONE)
*   **Day 13-14:** Integrate the local Big-Endian Phi-3 LLM to explain the routing decisions dynamically instead of using hardcoded strings.
*   **Day 15:** Code Freeze. Final End-to-End integration test across the live public IP.

---

### 🚨 THE MASTER INTEGRATION FLOW (OCT 16/17 DEPLOYMENT)
On October 16th/17th, Hack2Skill will revoke our Marist Cloud and give us the *official* competition IBM servers. Because we built this CI/CD pipeline, here is exactly what Pair 3 will do:
1. Connect via SSH using the provided credentials.
2. Run `git clone https://github.com/yuvrajlokhande19/Project-Syn-IBMZ.git`
3. Run `bash 03-mainframe-core/deploy_linuxone.sh`
4. Change the `MAINFRAME_URL` in Pair 1 and Pair 2's code to the new official IP.
5. **Win the Datathon in 10 minutes while other teams are still installing Python.**
