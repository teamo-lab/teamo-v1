#!/bin/bash
set -e

APP_DIR="/opt/teamo/instance-manager"
SERVICE_NAME="teamo-claude-proxy"

echo "=== Deploying Claude Code Proxy ==="

cd "$APP_DIR/claude-code-proxy"
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/${SERVICE_NAME}.service << 'SVCEOF'
[Unit]
Description=Teamo Claude Code Proxy
After=network.target teamo-instance-manager.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/teamo/instance-manager/claude-code-proxy
Environment=INSTANCE_MANAGER_URL=http://127.0.0.1:8900
Environment=PORT=8901
ExecStart=/opt/teamo/instance-manager/claude-code-proxy/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8901
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl restart ${SERVICE_NAME}

echo "=== Claude Code Proxy deployed on port 8901 ==="
systemctl status ${SERVICE_NAME} --no-pager
