#!/bin/bash
# VS Code Tunnel Setup for Remote Mobile Development
set -e

echo "🚀 Setting up VS Code Tunnel for mobile development..."

# Check if VS Code is installed
if ! command -v code &> /dev/null; then
    echo "📦 Installing VS Code..."
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
    sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list'
    sudo apt update
    sudo apt install -y code
    rm packages.microsoft.gpg
    echo "✅ VS Code installed"
else
    echo "✅ VS Code already installed"
fi

# Create systemd service
echo "📝 Creating systemd service..."
sudo tee /etc/systemd/system/code-tunnel.service > /dev/null <<EOF
[Unit]
Description=VS Code Tunnel
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
ExecStart=/usr/bin/code tunnel --accept-server-license-terms --name datingapp-dev
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service created"

# Initial authentication (interactive)
echo ""
echo "🔐 Starting tunnel for first-time authentication..."
echo "➡️  Please follow the prompts to authenticate with GitHub"
echo "➡️  After authentication completes, press Ctrl+C"
echo ""
read -p "Press Enter to continue..."

code tunnel --accept-server-license-terms --name datingapp-dev &
TUNNEL_PID=$!

echo ""
echo "⏳ Waiting for authentication to complete..."
echo "   Once you see the tunnel URL, press Ctrl+C to continue setup"
echo ""

# Wait for user to complete auth
wait $TUNNEL_PID 2>/dev/null || true

echo ""
echo "🔧 Enabling and starting systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable code-tunnel
sudo systemctl start code-tunnel

echo ""
echo "✅ VS Code Tunnel setup complete!"
echo ""
echo "📱 Access from Android:"
echo "   1. Open Chrome on your phone"
echo "   2. Navigate to: https://vscode.dev/tunnel/datingapp-dev"
echo "   3. Sign in with your GitHub account"
echo "   4. Open folder: /home/m/development/DatingApp"
echo ""
echo "🔍 Service Management:"
echo "   Status:  sudo systemctl status code-tunnel"
echo "   Logs:    sudo journalctl -u code-tunnel -f"
echo "   Restart: sudo systemctl restart code-tunnel"
echo "   Stop:    sudo systemctl stop code-tunnel"
echo ""
echo "🔗 Your tunnel URL: https://vscode.dev/tunnel/datingapp-dev"
echo ""
