import os, subprocess, hmac, hashlib, json, logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "change-me")
DEPLOY_SCRIPT = os.environ.get("DEPLOY_SCRIPT", "/home/a/datingapp/deploy.sh")
LOG_FILE = "/tmp/webhook-deploy.log"

def verify_signature(payload_body, signature_header):
    """Verify GitHub webhook signature."""
    if not signature_header:
        return False
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Verify signature
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(request.data, sig):
        app.logger.warning("Invalid signature")
        return jsonify({"error": "bad signature"}), 401

    event = request.headers.get("X-GitHub-Event", "")
    payload = request.json or {}

    if event == "ping":
        return jsonify({"ok": True, "msg": "pong"})

    if event == "push":
        branch = (payload.get("ref") or "").replace("refs/heads/", "")
        repo = payload.get("repository", {}).get("full_name", "unknown")
        app.logger.info(f"Push to {repo}/{branch}")

        # Deploy on main or develop pushes
        if branch in ("main", "develop"):
            app.logger.info(f"Triggering deploy for {branch}...")
            with open(LOG_FILE, "a") as f:
                f.write(f"\n=== Deploy triggered by {branch} push at {__import__('datetime').datetime.utcnow().isoformat()} ===\n")
            subprocess.Popen(
                ["bash", DEPLOY_SCRIPT],
                stdout=open(LOG_FILE, "a"),
                stderr=subprocess.STDOUT,
            )
            return jsonify({"ok": True, "deploy": "started"})

    return jsonify({"ok": True})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
