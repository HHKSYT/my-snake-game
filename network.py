import socket
import os
import threading
import sys
import json


port = 5555

class NetworkClient:
    def __init__(self,server,username):
        self.username = username
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server, port))
        self.other_scores = {}  # holds {player_id: score} received from server
        self.running = True
        self.lock = threading.Lock()
        self.send_score(0)

        # Start background thread to listen for server messages
        threading.Thread(target=self.listen_thread, daemon=True).start()

    def listen_thread(self):
        while self.running:
            try:
                data = self.sock.recv(4096)
                if data:
                    scores = json.loads(data.decode())
                    with self.lock:
                        self.other_scores = scores
                else:
                    break
            except Exception as e:
                print(f"[NetworkClient] Error in listen thread: {e}")
                break
        self.sock.close()

    def send_score(self, score):
        """
        Send the current player score to the server as JSON.
        """
        try:
            data = {
                "username": self.username,
                "score": score
            }
            self.sock.sendall(json.dumps(data).encode())
        except Exception as e:
            print(f"[NetworkClient] Error sending score: {e}")

    def get_scores(self):
        """
        Return a copy of the other players' scores.
        """
        with self.lock:
            return dict(self.other_scores)

    def stop(self):
        self.running = False
        self.sock.close()
