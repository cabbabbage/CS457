import socket
import json
import random
import struct
import zlib
import asyncio

from Tree import Tree
from Rabbit import Rabbit
from Bike import Bike

# Game constants
HOST = socket.gethostbyname(socket.gethostname())  # Get the local IP address
PORT = 38901

# Globals
players = []  # Shared list of player bikes
obstacles = []  # Shared list of obstacles
game_started = False  # Flag to indicate when the game has started

def game_setup():
    height = 1080
    width = 1920
    obstacles = [Tree(width, height) for _ in range(20)]
    obstacles.extend([Rabbit(width, height) for _ in range(4)])
    return obstacles

# Function to serialize game state in binary format
def serialize_game_state(game_state):
    bikes = [
        struct.pack(
            ">Ifii?",  # Format: int (id), float (score), int (x), int (y), bool (status)
            int(bike["id"]),
            float(bike["score"]),
            int(bike["position"]["x"]),
            int(bike["position"]["y"]),
            bool(bike["status"])
        ) for bike in game_state["bikes"]
    ]
    obstacles = [
        struct.pack(
            ">iII",  # Format: int (type), int (x), int (y)
            int(obstacle["type"]),  # Ensure "type" is an integer
            int(obstacle["position"]["x"]),  # Ensure "x" is an integer
            int(obstacle["position"]["y"])   # Ensure "y" is an integer
        ) for obstacle in game_state["obstacles"]
    ]
    return b''.join(bikes + obstacles)


# Compress data to reduce packet size
def compress_data(data):
    return zlib.compress(data)

async def handle_client(reader, writer):
    global game_started
    width, height = 1920, 1080
  
    player_bike = Bike(width, height, reader, writer)  # Pass `reader` and `writer`

    players.append(player_bike)  # Add bike to players list

    if not game_started:
        game_started = True

    running = True
    previous_state = None
    while running:
        if game_started:
            # Activate and update obstacles
            for obstacle in obstacles:
                if not obstacle.active:
                    obstacle.activate()
                    break
            for obstacle in obstacles:
                if obstacle.active:
                    obstacle.update()
                    print(str(obstacle.get_position()))
                    

        # Await `player_bike.update()` as it is now asynchronous
        await player_bike.update()
        player_bike.score += 0.1

        # Check for collisions
        for obstacle in obstacles:
            if obstacle.active:
                if (player_bike.hitbox_right > obstacle.hitbox_left and player_bike.hitbox_left < obstacle.hitbox_right):
                    if (player_bike.hitbox_bottom > obstacle.hitbox_top and player_bike.hitbox_top < obstacle.hitbox_bottom):
                        player_bike.active = False
                        running = False
                        break

        # Construct the game state
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

        # Send only delta if possible
        delta_state = game_state if previous_state is None else get_delta_state(game_state, previous_state)
        previous_state = game_state

        # Serialize and compress game state
        serialized_state = serialize_game_state(delta_state)
        compressed_state = compress_data(serialized_state)

        # Send compressed binary data to client
        try:
            writer.write(compressed_state)
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError):
            break

        await asyncio.sleep(1 / 20)  # Maintain the game tick rate

    players.remove(player_bike)
    writer.close()
    await writer.wait_closed()

def get_delta_state(current_state, previous_state):
    delta_state = {"bikes": [], "obstacles": []}
    for current_bike, previous_bike in zip(current_state["bikes"], previous_state["bikes"]):
        if current_bike["position"] != previous_bike["position"] or current_bike["status"] != previous_bike["status"]:
            delta_state["bikes"].append(current_bike)
    for current_obstacle, previous_obstacle in zip(current_state["obstacles"], previous_state["obstacles"]):
        if current_obstacle["position"] != previous_obstacle["position"]:
            delta_state["obstacles"].append(current_obstacle)
    return delta_state

async def start_server():
    global obstacles
    obstacles = game_setup()

    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"Server listening on {addr}")

    # Start the server and run indefinitely
    while True:
        await asyncio.sleep(3600)  # Keep the server running

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()
