import socket
import threading
import json

server = "192.168.99.121"
port = 5555

clients = []
scores = {}

def broadcast_scores():
    data = json.dumps(scores).encode()
    for client in clients:
        try:
            client.sendall(data)
        except Exception:
            pass

def handle_client(conn,addr):

    global scores
    clients.append(conn)

    try:
        data = conn.recv(2048)
        if not data:
            return

        msg = json.loads(data.decode())
        username = msg.get("username", str(addr))
        scores[username] = msg.get("score", 0)

        broadcast_scores()
        
        while True:    
            data = conn.recv(2048)
            if not data:
                break

            try:
                msg = json.loads(data.decode())
                if "score" in msg:
                    scores[username] = msg["score"]
                    broadcast_scores()
            except Exception as e:
                print(f"Error parsing data from {username}:", {e})
    finally:
        clients.remove(conn)
        scores.pop(username,None)
        broadcast_scores()
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((server,port))
        s.listen()
        print(f"Server listening on {server}:{port}")

        while True:
            conn,addr = s.accept()
            print(f"Client connected from {addr}")
            threading.Thread(target=handle_client, args=(conn,addr), daemon=True).start()

if __name__ == "__main__":
    main()