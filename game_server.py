import socket
import json
import random
import time
from threading import Thread

from Tree import Tree
from Rabbit import Rabbit
from Bike import Bike

# Game constants
HOST = 'localhost'
PORT = 5555

def handle_client(client_socket):
    print("Client connected.")
    data = client_socket.recv(1024).decode("utf-8")
    height,   width, = json.loads(data)

    # Instantiate game entities, passing client_socket to Bike
    obstacles = [Tree(width, height) for _ in range(20)]
    obstacles.extend([Rabbit(width, height) for _ in range(4)])
    player_bike = Bike(width, height, client_socket)


    print(f"[DEBUG] Game entities initialized. Total obstacles: {len(obstacles)}")

    running = True
    while running:
        # Activate an inactive obstacle
        for obstacle in obstacles:
            if not obstacle.active:
                obstacle.activate()
                print(f"[DEBUG] Activated obstacle of type {obstacle.type} at position ({obstacle.x}, {obstacle.y})")
                break

        # Update obstacles
        for obstacle in obstacles:
            if obstacle.active:
                obstacle.update()
                print(f"[DEBUG] Updated obstacle of type {obstacle.type} at position ({obstacle.x}, {obstacle.y})")

        # Update bike
        player_bike.update()
        player_bike.score += 0.1
        print(f"[DEBUG] Updated bike position to ({player_bike.x}, {player_bike.y}), score: {player_bike.score}")

        # Check for collisions
        for obstacle in obstacles:
            if obstacle.active:
                if (player_bike.hitbox_right > obstacle.hitbox_left and player_bike.hitbox_left < obstacle.hitbox_right):
                    if (player_bike.hitbox_bottom > obstacle.hitbox_top and player_bike.hitbox_top < obstacle.hitbox_bottom):
                        print("[DEBUG] Collision detected!")
                        player_bike.active = False
                        running = False
                        break

        # Prepare game state as JSON
        game_state = {
            "bike": {
                "type": player_bike.type,
                "position": {"x": player_bike.x, "y": player_bike.y},
                "score": player_bike.score,
                "status": player_bike.active
            },
            "obstacles": [
                {"type": obstacle.type, "position": {"x": obstacle.x, "y": obstacle.y}}
                for obstacle in obstacles if obstacle.active
            ],
            "game_over": not player_bike.active  # True if the game has ended
        }
        print(f"[DEBUG] Game state prepared: {game_state}")

        # Send game state to client
        try:
            client_socket.sendall(json.dumps(game_state).encode("utf-8"))
            print(f"[DEBUG] Game state sent to client: {json.dumps(game_state)}")
        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"[ERROR] Failed to send data to client: {e}")
            return

        time.sleep(1 / 40)  # Control the frame rate

    client_socket.close()
    print("Client disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"[DEBUG] Client connected from {addr}")
        client_thread = Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
