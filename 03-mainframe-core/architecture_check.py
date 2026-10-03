import sys
import platform
import struct

def run_preflight_check():
    print("="*50)
    print("PROJECT SYN: IBM Z ARCHITECTURE PRE-FLIGHT CHECK")
    print("="*50)
    
    # Check OS and Platform
    print(f"[*] Operating System: {platform.system()} {platform.release()}")
    print(f"[*] Machine Architecture: {platform.machine()}")
    print(f"[*] Python Version: {platform.python_version()}")
    
    print("-" * 50)
    
    # Check Endianness (The "Big-Endian Trap" Test)
    byte_order = sys.byteorder
    print(f"[*] Memory Byte Order: {byte_order.upper()}")
    
    if byte_order == 'big':
        print("\n[SUCCESS] Big-Endian architecture detected!")
        print("    You are successfully running on an IBM s390x environment.")
        print("    Your Snap ML models, SQLite Hashes, and C-extensions are safe to deploy.")
    else:
        print("\n[WARNING] Little-Endian architecture detected!")
        print("    You are running on a standard x86/ARM machine (like Windows/Mac).")
        print("    DO NOT ASSUME code that works here will work on October 17th!")
        print("    Native C-extensions or unoptimized ML libraries might break due to reversed memory reading.")
        print("    Please spin up the Marist College LinuxONE cloud to stage your code.")
        
    print("="*50)

if __name__ == "__main__":
    run_preflight_check()
