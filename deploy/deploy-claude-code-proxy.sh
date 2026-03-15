#!/bin/bash
set -e

APP_DIR="/opt/teamo/instance-manager"
SERVICE_NAME="teamo-claude-code-proxy"
PROXY_PORT=8901

echo "=== Deploying Claude Code Proxy ==="

# Install dependencies
apt-get update -qq
apt-get install -y -qq python3-pip python3-venv git

# Install MongoDB (for conversation history)
if ! command -v mongod &> /dev/null; then
    echo "=== Installing MongoDB 7.0 ==="
    apt-get install -y -qq gnupg curl
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/7.0 main" > /etc/apt/sources.list.d/mongodb-org-7.0.list
    apt-get update -qq
    apt-get install -y -qq mongodb-org
    systemctl enable mongod
    systemctl start mongod
    echo "MongoDB installed and started"
else
    echo "MongoDB already installed"
    systemctl is-active --quiet mongod || systemctl start mongod
fi

# Clone or update repo
if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR" && git pull origin main
else
    rm -rf "$APP_DIR"
    git clone https://github.com/teamo-lab/teamo-v1.git "$APP_DIR"
fi

# Setup Python venv for proxy
cd "$APP_DIR/claude-code-proxy"
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/${SERVICE_NAME}.service << 'SVCEOF'
[Unit]
Description=Teamo Claude Code Proxy
After=network.target mongod.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/teamo/instance-manager/claude-code-proxy
Environment=INSTANCE_MANAGER_URL=http://127.0.0.1:8902
Environment=LEGACY_BACKEND_URL=http://43.159.4.84:59815
Environment=MONGODB_URI=mongodb://localhost:27017
Environment=MONGODB_DB=wowchat
ExecStart=/opt/teamo/instance-manager/claude-code-proxy/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8901
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

echo "=== Claude Code Proxy deployed on port ${PROXY_PORT} ==="
systemctl status ${SERVICE_NAME} --no-pager

# Quick smoke test
sleep 2
echo ""
echo "=== Smoke test ==="
curl -sf http://127.0.0.1:${PROXY_PORT}/docs > /dev/null && echo "Proxy /docs: OK" || echo "Proxy /docs: FAIL"
echo "=== Done ==="
