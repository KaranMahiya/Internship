from flask import Flask, request, jsonify # type: ignore
import time
import threading
import os

app = Flask(__name__)

clients = {}

TIMEOUT = 30  # seconds

def cleanup_clients():
    while True:
        now = time.time()
        to_delete = []

        for cid in clients:
            if now - clients[cid]["last_seen"] > TIMEOUT:
                to_delete.append(cid)

        for cid in to_delete:
            print(f"[CLEANUP] Removing {cid}")
            del clients[cid]

        time.sleep(5)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    client_id = data["id"]
    ip = request.remote_addr

    clients[client_id] = {
        "ip": ip,
        "last_seen": time.time()
    }

    print(f"[REGISTER] {client_id} -> {ip}")
    return jsonify({"status": "registered"})

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json
    client_id = data["id"]

    if client_id in clients:
        clients[client_id]["last_seen"] = time.time()
        return jsonify({"status": "alive"})

    return jsonify({"error": "not registered"}), 400

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    sender = data["from"]
    target = data["to"]
    message = data["message"]

    if target not in clients:
        return jsonify({"error": "target not found"}), 404

    print(f"[ROUTE] {sender} -> {target}")

    return jsonify({
        "from": sender,
        "to": target,
        "message": message
    })

@app.route("/healthz")
def health():
    return "OK", 200


if __name__ == "__main__":
    threading.Thread(target=cleanup_clients, daemon=True).start()

    port = int(os.environ.get("PORT", 10000))  # 🔥 FIX
    app.run(host="0.0.0.0", port=port)

@app.route("/")
def home():
    return "Server is running 🚀"
