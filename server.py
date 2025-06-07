import socket
import threading
import json

server = "192.168.99.230"
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
    player_id = str(addr)
    scores[player_id] = 0

    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break
            try:
                msg = json.loads(data.decode())
                if "score" in msg:
                    scores[player_id] = msg["score"]
                    broadcast_scores()
            except Exception as e:
                print(f"error parsing data from {player_id}: {e}")
    finally:
        clients.remove(conn)
        scores.pop(player_id,None)
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