# 📱 Remote Mobile Development Setup
*Work on DatingApp from Android with full Copilot support*

## 🎯 Goal
Enable spec-driven development workflow from Android phone, accessing this Ubuntu laptop remotely with full GitHub Copilot assistance.

## 🏗️ Architecture
```
Android Phone (VS Code Mobile/Browser)
    ↓ (SSH/HTTPS)
Ubuntu Laptop (code-server or VS Code tunnel)
    ↓
DatingApp workspace with Copilot extension
```

## ⚙️ Setup Options

### **Option 1: GitHub.dev + Codespaces (Recommended for Mobile)**
*Best experience on mobile browsers, native Copilot support*

#### Setup on Ubuntu Laptop:
```bash
# Ensure git is configured
git config --global user.name "your-name"
git config --global user.email "your-email"

# Push any local changes
cd /home/m/development/DatingApp
git add .
git commit -m "Sync before mobile setup"
git push origin 001-mvp-foundation
```

#### On Android:
1. Open Chrome/Firefox on your phone
2. Navigate to `https://github.dev/best-koder-ever/DatingApp-Config/tree/001-mvp-foundation`
3. Sign in with your GitHub account
4. Install GitHub Copilot extension in the web editor
5. Work with full Copilot Chat, file editing, terminal access

**Pros:** Native Copilot, no server maintenance, works anywhere
**Cons:** Requires internet, limited to cloud environment

---

### **Option 2: VS Code Tunnel (Remote Development)**
*Direct connection to your Ubuntu laptop with full local environment*

#### Setup on Ubuntu Laptop:
```bash
# Install VS Code if not already installed
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install code

# Start VS Code tunnel (creates secure connection to Microsoft servers)
code tunnel --accept-server-license-terms

# Follow the prompts to authenticate with GitHub
# Get the tunnel name (e.g., "your-laptop-name")
```

#### Keep Laptop Awake & Accessible:
```bash
# Prevent sleep when lid closed (optional)
sudo nano /etc/systemd/logind.conf
# Set: HandleLidSwitch=ignore
sudo systemctl restart systemd-logind

# Keep services running
cd /home/m/development/DatingApp
./infrastructure/start.sh
./dev-start.sh
```

#### Create systemd service to auto-start tunnel:
```bash
sudo nano /etc/systemd/system/code-tunnel.service
```

Add:
```ini
[Unit]
Description=VS Code Tunnel
After=network.target

[Service]
Type=simple
User=m
WorkingDirectory=/home/m
ExecStart=/usr/bin/code tunnel --accept-server-license-terms
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable it:
```bash
sudo systemctl enable code-tunnel
sudo systemctl start code-tunnel
sudo systemctl status code-tunnel
```

#### On Android:
1. Open Chrome on your phone
2. Go to `https://vscode.dev/tunnel/<your-tunnel-name>`
3. Sign in with your GitHub account
4. Install GitHub Copilot extension
5. Open `/home/m/development/DatingApp` folder
6. Work with full access to local environment

**Pros:** Full local environment, Docker containers accessible, fast
**Cons:** Laptop must stay on and connected

---

### **Option 3: code-server (Self-Hosted VS Code)**
*Run VS Code in browser on your own server*

#### Setup on Ubuntu Laptop:
```bash
# Install code-server
curl -fsSL https://code-server.dev/install.sh | sh

# Configure
mkdir -p ~/.config/code-server
cat > ~/.config/code-server/config.yaml <<EOF
bind-addr: 0.0.0.0:8443
auth: password
password: $(openssl rand -base64 32)
cert: false
EOF

# Note the password from config
cat ~/.config/code-server/config.yaml | grep password

# Start code-server
sudo systemctl enable --now code-server@$USER

# Install Copilot extension
code-server --install-extension GitHub.copilot
code-server --install-extension GitHub.copilot-chat
```

#### Secure Access (choose one):

**A. Tailscale (Recommended - Zero Config VPN)**
```bash
# On Ubuntu
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# On Android
# Install Tailscale app from Play Store
# Sign in with same account
# Access: http://<tailscale-ip>:8443
```

**B. Cloudflare Tunnel (Public Access)**
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create tunnel
cloudflared tunnel login
cloudflared tunnel create datingapp-dev
cloudflared tunnel route dns datingapp-dev dev.yourdomain.com
cloudflared tunnel run --url http://localhost:8443 datingapp-dev
```

#### On Android:
1. Open Chrome
2. Navigate to your access URL (Tailscale IP or Cloudflare domain)
3. Enter the password from config.yaml
4. Work with full Copilot support

**Pros:** Full control, works offline (with Tailscale), customizable
**Cons:** More setup, manual updates

---

## 🚀 Recommended Workflow

### **For Quick Edits & Chat:**
Use **GitHub.dev** - instant access, no server setup

### **For Full Development:**
Use **VS Code Tunnel** - best balance of convenience and power

### **For Offline Work:**
Use **code-server + Tailscale** - works without internet after initial setup

---

## 📱 Mobile Optimization Tips

### **Browser Settings:**
- Enable "Desktop Site" mode in Chrome for better layout
- Use landscape orientation for more screen space
- Install "Desktop by xda" app for forced desktop mode

### **Keyboard Setup:**
- Use Bluetooth keyboard for serious coding
- Enable SwiftKey or Gboard with coding shortcuts
- Consider Termux app for git operations alongside browser

### **Efficient Spec-Driven Development:**
1. Open spec files (`specs/001-mvp-foundation/tasks.md`) in one tab
2. Use Copilot Chat to discuss implementation in another
3. Edit files with Copilot suggestions
4. Run tests via integrated terminal
5. Commit directly from mobile browser

### **Keep Services Running:**
```bash
# Create tmux session for services
sudo apt install tmux
tmux new -s datingapp

# In tmux, start services
cd /home/m/development/DatingApp
./infrastructure/start.sh
./dev-start.sh

# Detach: Ctrl+B, then D
# Reattach later: tmux attach -t datingapp
```

---

## ✅ Verification Steps

1. **Test tunnel/server access** from Android browser
2. **Open DatingApp workspace** in remote VS Code
3. **Verify Copilot works** - type a comment and get suggestions
4. **Test terminal** - run `./dev-status.sh`
5. **Edit a file** - make a change and commit via Source Control panel
6. **Run tests** - execute `python3 api_tests.py` from terminal

---

## 🔒 Security Checklist

- ✅ Use strong passwords for code-server
- ✅ Keep Ubuntu laptop encrypted (LUKS)
- ✅ Enable UFW firewall: `sudo ufw enable`
- ✅ Use Tailscale or Cloudflare Tunnel instead of exposing ports
- ✅ Keep laptop physically secure
- ✅ Enable automatic security updates:
  ```bash
  sudo apt install unattended-upgrades
  sudo dpkg-reconfigure -plow unattended-upgrades
  ```
- ✅ Regular backups of workspace:
  ```bash
  # Add to crontab
  0 2 * * * rsync -av /home/m/development/DatingApp /backup/location/
  ```

---

## 🎯 Quick Start (Fastest Path)

**Right Now (5 minutes):**
1. Push your code: `git push origin 001-mvp-foundation`
2. On Android, open: `https://github.dev/best-koder-ever/DatingApp-Config`
3. Install Copilot extension
4. Start coding!

**Tonight (30 minutes):**
1. Set up VS Code tunnel on Ubuntu (follow Option 2)
2. Access from Android: `https://vscode.dev/tunnel/<name>`
3. Full local environment + Copilot

**This Weekend (if you want offline capability):**
1. Install Tailscale on both devices
2. Set up code-server with Tailscale access
3. Work anywhere, even without internet

---

## 📚 Resources

- VS Code Tunnel docs: https://code.visualstudio.com/docs/remote/tunnels
- code-server: https://coder.com/docs/code-server
- Tailscale: https://tailscale.com/kb/
- GitHub Copilot on web: https://github.com/features/copilot

---

## 🐛 Troubleshooting

**Can't connect to tunnel:**
- Verify laptop is on and connected: `systemctl status code-tunnel`
- Check tunnel status: `code tunnel status`
- Restart: `sudo systemctl restart code-tunnel`

**Copilot not working:**
- Sign out and sign back in to GitHub
- Reinstall extension: `code-server --install-extension GitHub.copilot --force`
- Check subscription: https://github.com/settings/copilot

**Services not accessible:**
- Verify containers running: `cd /home/m/development/DatingApp && docker ps`
- Check if services started: `./dev-status.sh`
- Restart: `./dev-stop.sh && ./dev-start.sh`

**Mobile browser issues:**
- Clear browser cache
- Try different browser (Firefox, Edge)
- Enable desktop site mode
- Use landscape orientation

---

Let me know which option you want to pursue and I can help with the detailed setup!
