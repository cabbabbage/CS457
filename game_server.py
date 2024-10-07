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
width, height = 800, 600  # Example screen size (adjust as needed)

# Initialize server
def handle_client(client_socket):
    print("Client connected.")
    
    # Instantiate game entities, passing client_socket to Bike
    obstacles = [Tree() for _ in range(20)]
    obstacles.extend([Rabbit() for _ in range(4)])
    player_bike = Bike(width, height, client_socket)

    running = True
    while running:
        for obstacle in obstacles:
            if not obstacle.active:
                obstacle.activate()
                break

        # Update obstacles
        for obstacle in obstacles:
            if obstacle.active:
                obstacle.update()

        # Update bike
        player_bike.update()
        player_bike.score += 0.1

        # Check for collisions
        for obstacle in obstacles:
            if obstacle.active:
                if (player_bike.hitbox_right > obstacle.hitbox_left and player_bike.hitbox_left < obstacle.hitbox_right):
                    if (player_bike.hitbox_bottom > obstacle.hitbox_top and player_bike.hitbox_top < obstacle.hitbox_bottom):
                        print("Collision detected!")
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

        # Send game state to client
        client_socket.sendall(json.dumps(game_state).encode("utf-8"))
        time.sleep(1 / 40)  # Control the frame rate

    client_socket.close()
    print("Client disconnected.")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("Server listening on {}:{}".format(HOST, PORT))

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


if __name__ == "__main__":
    start_server()