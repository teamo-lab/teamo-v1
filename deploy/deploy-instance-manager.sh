#!/bin/bash
set -e

APP_DIR="/opt/teamo/instance-manager"
INSTANCE_DIR="/opt/teamo/instances"
SERVICE_NAME="teamo-instance-manager"
REPO_URL="https://github.com/teamo-lab/teamo-v1.git"

echo "=== Deploying Teamo Instance Manager ==="

# Install dependencies
apt-get update -qq
apt-get install -y -qq python3-pip python3-venv git

# Clone or update repo
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR" && git pull origin main
else
    rm -rf "$APP_DIR"
    git clone "$REPO_URL" "$APP_DIR"
fi

# Create instance directory
mkdir -p "$INSTANCE_DIR"

# Setup Python venv
cd "$APP_DIR/instance-manager"
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/${SERVICE_NAME}.service << 'SVCEOF'
[Unit]
Description=Teamo Instance Manager
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/teamo/instance-manager/instance-manager
Environment=INSTANCE_BASE_DIR=/opt/teamo/instances
Environment=CLAUDE_BIN=/root/.nvm/versions/node/v22.22.0/bin/claude
Environment=CLAUDE_TIMEOUT_SECONDS=300
Environment=PORT=8902
ExecStart=/opt/teamo/instance-manager/instance-manager/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8902
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

echo "=== Instance Manager deployed on port 8900 ==="
systemctl status ${SERVICE_NAME} --no-pager
