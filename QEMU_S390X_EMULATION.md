# 🖥️ Local s390x Emulation Guide (No Cloud Needed!)

If you cannot access the IBM LinuxONE Cloud or are waiting for approval, **you can emulate the IBM Mainframe directly on your Windows laptop** using Docker and QEMU.

This allows you to test for the "Big-Endian Trap" locally without needing a real IBM server.

## How to emulate s390x locally on Windows/Mac:

### Step 1: Install Docker Desktop
Ensure you have Docker Desktop installed on your laptop. (It includes QEMU emulation natively).

### Step 2: Enable Multi-Architecture Builders
Open your terminal (Command Prompt or PowerShell) and run:
```bash
docker run --privileged --rm tonistiigi/binfmt --install all
```
*This tells your computer how to translate IBM s390x processor instructions to your Intel/AMD processor.*

### Step 3: Build the Mainframe Core for s390x
Navigate to your project folder and tell Docker to build specifically for the IBM architecture (`linux/s390x`):
```bash
docker buildx build --platform linux/s390x -t syn-mainframe-s390x ./03-mainframe-core
```

### Step 4: Run the Emulated Mainframe
```bash
docker run --platform linux/s390x -p 8000:8000 syn-mainframe-s390x
```

**Result:** You are now running an emulated IBM Z processor on your laptop! If your Python ML models and C-extensions boot up successfully here, they are guaranteed to work on the real IBM server on October 17th.
