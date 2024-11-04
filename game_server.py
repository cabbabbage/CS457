import socket
import json
import time
from threading import Thread, Lock

from Tree import Tree
from Rabbit import Rabbit
from Bike import Bike

# Game constants
HOST = socket.gethostbyname(socket.gethostname())  # Get the local IP address
PORT = 0  # Let the OS pick an available port

# Globals
players = []  # Shared list of player bikes
obstacles = []  # Shared list of obstacles
lock = Lock()  # Lock to handle shared resources

def game_setup():
    height = 1080
    width = 1920
    obstacles = [Tree(width, height) for _ in range(20)]
    obstacles.extend([Rabbit(width, height) for _ in range(4)])
    return obstacles

def game_loop():
    """Continuously updates the game state, even if no players are connected."""
    global obstacles
    while True:
        # Update obstacles
        with lock:
            for obstacle in obstacles:
                if not obstacle.active:
                    obstacle.activate()
                    if obstacle.active:
                        print(f"[DEBUG] Activated obstacle of type {obstacle.type} at position ({obstacle.x}, {obstacle.y})")
                    break

            # Move active obstacles
            for obstacle in obstacles:
                if obstacle.active:
                    obstacle.update()
                    #print(f"[DEBUG] Updated obstacle of type {obstacle.type} at position ({obstacle.x}, {obstacle.y})")

            # Update player bikes
            for player_bike in players:
                if player_bike.active:
                    player_bike.update()
                    player_bike.score += 0.1
                    print(f"[DEBUG] Updated bike position to ({player_bike.x}, {player_bike.y}), score: {player_bike.score}")

                    # Check for collisions
                    for obstacle in obstacles:
                        if obstacle.active and (
                            player_bike.hitbox_right > obstacle.hitbox_left
                            and player_bike.hitbox_left < obstacle.hitbox_right
                            and player_bike.hitbox_bottom > obstacle.hitbox_top
                            and player_bike.hitbox_top < obstacle.hitbox_bottom
                        ):
                            print("[DEBUG] Collision detected!")
                            player_bike.active = False
                            break

        time.sleep(1 / 40)  # Control the frame rate

def handle_client(client_socket, addr):
    """Handles each client connection and sends game state updates."""
    width, height = 1920, 1080
    player_bike = Bike(width, height, client_socket, addr)

    with lock:
        players.append(player_bike)  # Add bike to players list
        print(f"[DEBUG] Player bike added. Total players: {len(players)}")

    running = True
    while running:
        # Prepare game state as JSON
        with lock:
            game_state = {
                "bikes": [
                    {
                        "type": bike.type,
                        "position": {"x": bike.x, "y": bike.y},
                        "score": bike.score,
                        "status": bike.active,
                        "ip": bike.client_ip  # Note: This isn't secure; consider alternatives for production
                    } for bike in players
                ],
                "obstacles": [
                    {"type": obstacle.type, "position": {"x": obstacle.x, "y": obstacle.y}}
                    for obstacle in obstacles if obstacle.active
                ],
                "game_over": not player_bike.active  # True if the game has ended for this player
            }
            print(f"[DEBUG] Game state prepared for client: {addr}")

        # Send game state to client
        try:
            client_socket.sendall(json.dumps(game_state).encode("utf-8"))
            print(f"[DEBUG] Game state sent to client: {addr}")
        except (ConnectionResetError, BrokenPipeError) as e:
            print(f"[ERROR] Failed to send data to client: {e}")
            break

        time.sleep(1 / 40)  # Control the frame rate

    # Clean up when client disconnects
    with lock:
        players.remove(player_bike)
        print(f"Client {addr} disconnected.")
    client_socket.close()

def start_server():
    global obstacles
    obstacles = game_setup()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    # Retrieve the assigned IP address and port
    server_ip, server_port = server_socket.getsockname()
    print(f"Server listening on {server_ip}:{server_port}")

    # Start the game loop in a separate thread
    game_thread = Thread(target=game_loop, daemon=True)
    game_thread.start()

    # Accept clients and start game
    while True:
        client_socket, addr = server_socket.accept()
        print(f"[DEBUG] Client connected from {addr}")
        client_thread = Thread(target=handle_client, args=(client_socket, addr,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
