# 🤖 AI AGENT INSTRUCTION PROTOCOL

## IDENTITY CHECK
1. YOU MUST DETERMINE WHICH TEAM YOU ARE WORKING WITH.
2. ASK THE USER: "Which team are you in? Pair 1 (Frontend), Pair 2 (Data Logic), or Pair 3 (Mainframe Core)?" (Or infer from context).
3. YOU MUST NOT TOUCH ANY FOLDERS OUTSIDE OF YOUR PAIR'S DESIGNATED DOMAIN.

## SEQUENTIAL TASK EXECUTION (LEVELING SYSTEM)
Do NOT complete all tasks at once. You must follow the exact sequence defined in the Task files.
1. Read `Task_1*.txt`. Implement and verify it perfectly.
2. ONLY after the user confirms Task 1 is complete, proceed to read and execute Task 2.
3. This is a leveled system to prevent execution crashes and hallucination overload.

## REAL-WORLD SIMULATION
Do not generate simple `random.randint` fake data. Simulate realistic mathematical distributions (e.g., Perlin noise for floods, sine waves for grid voltage).

## KNOWLEDGE INTEGRATION
You must read the `datathon.txt`, `gemini-code*.txt`, and the PDF guides in this folder to understand the full context of "Project Syn" and IBM Z s390x constraints.
