import socket
import threading
import time
import json

HOST = "0.0.0.0"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

clients = {}  # {client_id: (ip, port, last_seen)}

TIMEOUT = 30  # seconds


def cleanup_clients():
    while True:
        now = time.time()
        to_delete = []
        for cid, (ip, port, last_seen) in clients.items():
            if now - last_seen > TIMEOUT:
                to_delete.append(cid)

        for cid in to_delete:
            print(f"[CLEANUP] Removing inactive client {cid}")
            del clients[cid]

        time.sleep(5)


def handle_message(data, addr):
    try:
        msg = json.loads(data.decode())
        msg_type = msg.get("type")

        if msg_type == "register":
            client_id = msg["id"]
            clients[client_id] = (addr[0], addr[1], time.time())
            print(f"[REGISTER] {client_id} -> {addr}")

        elif msg_type == "heartbeat":
            client_id = msg["id"]
            if client_id in clients:
                ip, port, _ = clients[client_id]
                clients[client_id] = (ip, port, time.time())
                print(f"[HEARTBEAT] {client_id}")

        elif msg_type == "send":
            target = msg["to"]
            sender = msg["from"]
            message = msg["message"]

            if target in clients:
                target_addr = (clients[target][0], clients[target][1])

                forward_msg = {
                    "type": "message",
                    "from": sender,
                    "message": message
                }

                server.sendto(json.dumps(forward_msg).encode(), target_addr)
                print(f"[ROUTE] {sender} -> {target}")

            else:
                print(f"[ERROR] Target {target} not found")

    except Exception as e:
        print("[ERROR]", e)


def start_server():
    print(f"Server running on {HOST}:{PORT}")
    threading.Thread(target=cleanup_clients, daemon=True).start()

    while True:
        data, addr = server.recvfrom(1024)
        threading.Thread(target=handle_message, args=(data, addr)).start()


if __name__ == "__main__":
    start_server()
