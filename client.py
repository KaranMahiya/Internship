import socket
import threading
import json
import time

SERVER_IP = "YOUR_SERVER_IP"
SERVER_PORT = 5000

client_id = input("Enter your client ID: ")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send(data):
    sock.sendto(json.dumps(data).encode(), (SERVER_IP, SERVER_PORT))


def register():
    send({
        "type": "register",
        "id": client_id
    })


def heartbeat():
    while True:
        send({
            "type": "heartbeat",
            "id": client_id
        })
        time.sleep(10)


def receive():
    while True:
        data, _ = sock.recvfrom(1024)
        msg = json.loads(data.decode())
        print(f"\n📩 Message from {msg['from']}: {msg['message']}")


def send_message():
    while True:
        target = input("Send to: ")
        message = input("Message: ")

        send({
            "type": "send",
            "from": client_id,
            "to": target,
            "message": message
        })


register()

threading.Thread(target=heartbeat, daemon=True).start()
threading.Thread(target=receive, daemon=True).start()

send_message()
