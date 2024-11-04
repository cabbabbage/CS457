import socket
import json
import random
import time
from threading import Thread, Lock

from Tree import Tree
from Rabbit import Rabbit
from Bike import Bike

# Game constants
import socket
import json

HOST = socket.gethostbyname(socket.gethostname())
PORT = 45412

# Setup server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

# Retrieve the assigned IP address and port
server_ip, server_port = server_socket.getsockname()

# Save IP and port to a JSON file
with open("server_info.json", "w") as file:
    json.dump({"ip": server_ip, "port": server_port}, file)

print(f"Server listening on {server_ip}:{server_port}")

# Globals
players = []  # Shared list of player bikes
obstacles = []  # Shared list of obstacles
game_started = False  # Flag to indicate when the game has started
lock = Lock()  # Lock to handle shared resources

def game_setup():
    height = 1080
    width = 1920
    obstacles = [Tree(width, height) for _ in range(20)]
    obstacles.extend([Rabbit(width, height) for _ in range(4)])
    return obstacles

def handle_client(client_socket, addr):
    global game_started
    width, height = 1920, 1080
  
    player_bike = Bike(width, height, client_socket, addr)

    with lock:
        players.append(player_bike)  # Add bike to players list

    with lock:
        if not game_started:
            game_started = True

    running = True
    while running:
        if game_started:
            for obstacle in obstacles:
                if not obstacle.active:
                    obstacle.activate()

                    break

            for obstacle in obstacles:
                if obstacle.active:
                    obstacle.update()

        player_bike.update()
        player_bike.score += 0.1

        for obstacle in obstacles:
            if obstacle.active:
                if (player_bike.hitbox_right > obstacle.hitbox_left and player_bike.hitbox_left < obstacle.hitbox_right):
                    if (player_bike.hitbox_bottom > obstacle.hitbox_top and player_bike.hitbox_top < obstacle.hitbox_bottom):
                        player_bike.active = False
                        running = False
                        break

        game_state = {
            "bikes": [
                {
                    "type": bike.type,
                    "position": {"x": bike.x, "y": bike.y},
                    "score": bike.score,
                    "status": bike.active,
                    "id": bike.id
                } for bike in players
            ],
            "obstacles": [
                {"type": obstacle.type, "position": {"x": obstacle.x, "y": obstacle.y}}
                for obstacle in obstacles if obstacle.active
            ],
            "game_over": not player_bike.active
        }

        try:
            client_socket.sendall(json.dumps(game_state).encode("utf-8"))
        except (ConnectionResetError, BrokenPipeError):
            break

        time.sleep(1 / 20)  

    with lock:
        players.remove(player_bike)

    client_socket.close()

def start_server():
    global obstacles
    obstacles = game_setup()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    server_ip, server_port = server_socket.getsockname()
    print(f"Server listening on {server_ip}:{server_port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = Thread(target=handle_client, args=(client_socket, addr,))
        client_thread.start()

if __name__ == "__main__":
    start_server()
