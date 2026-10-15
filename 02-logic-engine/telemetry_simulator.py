"""
Project Syn // AEGISCORE Telemetry Simulator Launcher Shim
Delegates execution to 02-logic-engine/src/telemetry_simulator.py
Ensures compatibility with START_PROJECT_SYN.bat and top-level execution.
"""
import os
import sys
import importlib.util

_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "telemetry_simulator.py")
_spec = importlib.util.spec_from_file_location("telemetry_simulator_core", _src_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

def main():
    _mod.main()

if __name__ == "__main__":
    main()
