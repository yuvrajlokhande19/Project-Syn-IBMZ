#!/bin/bash
# ==============================================================================
# PROJECT SYN // AEGISCORE: ZERO-TOUCH HOSPITAL KIOSK INSTALLER (LINUX)
# Target: Hospital Wall Displays, Crash Cart Thin Clients, Emergency Command Hubs
# ==============================================================================

set -e

echo "================================================================================"
echo "    AEGISCORE // ZERO-TOUCH HOSPITAL KIOSK INSTALLER"
echo "    Automatic Boot directly into Fullscreen Disaster Cockpit (No CLI/Mouse)"
echo "================================================================================"

# 1. Install Kiosk packages (X11, Chromium or Cage/Wayland, unclutter to hide mouse)
echo "[1/4] Installing Display Server & Kiosk Engine packages..."
sudo apt-get update -y
sudo apt-get install -y xorg openbox chromium-browser unclutter curl

# 2. Configure Openbox Kiosk Autostart
echo "[2/4] Configuring Autostart Kiosk Environment..."
mkdir -p ~/.config/openbox

cat << 'EOF' > ~/.config/openbox/autostart
# Disable screen sleep & DPMS energy savings for 24/7 hospital monitoring
xset s off
xset s noblank
xset -dpms

# Hide mouse cursor when inactive (touch screen mode)
unclutter -idle 0.5 -root &

# Launch Chromium in Fullscreen Kiosk Mode pointing to AegisCore
sed -i 's/"exited_cleanly":false/"exited_cleanly":true/' ~/.config/chromium/'Local State' || true
sed -i 's/"exit_type":"Crashed"/"exit_type":"Normal"/' ~/.config/chromium/Default/Preferences || true

chromium-browser \
    --noerrdialogs \
    --disable-infobars \
    --kiosk \
    --check-for-update-interval=31536000 \
    --overscroll-history-navigation=0 \
    --disable-pinch \
    "http://127.0.0.1:8000/ui/?kiosk=true&nocursor=true" &
EOF

chmod +x ~/.config/openbox/autostart

# 3. Create Systemd Service for AegisCore Kiosk
echo "[3/4] Creating systemd service: aegiscore-kiosk.service..."
CURRENT_USER=$(whoami)

sudo tee /etc/systemd/system/aegiscore-kiosk.service > /dev/null << EOF
[Unit]
Description=AegisCore Disaster Command Center - Zero-Touch Hospital Kiosk
After=network.target sound.target

[Service]
User=$CURRENT_USER
Environment=DISPLAY=:0
ExecStart=/usr/bin/startx /usr/bin/openbox-session
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo "       aegiscore-kiosk.service generated."

echo "[4/4] Verification & Activation Instructions:"
echo "================================================================================"
echo "To enable Auto-Boot on power-on (zero human commands):"
echo "  sudo systemctl enable aegiscore-kiosk.service"
echo "  sudo systemctl start aegiscore-kiosk.service"
echo ""
echo "When plugged into an HDMI monitor or hospital wall display, the screen will"
echo "boot straight into the trilingual AegisCore disaster matrix without a mouse!"
echo "================================================================================"
