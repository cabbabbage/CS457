import socket
import json
import random
import time
import argparse
from threading import Thread, Lock

from Tree import Tree
from Rabbit import Rabbit
from Bike import Bike

# Globals
players = []  # Shared list of player bikes
obstacles = []  # Shared list of obstacles
game_started = False  # Flag to indicate when the game has started
lock = Lock()
run_state = 3  # Default to waiting for players

# States:
# 0: Running (normal gameplay loop)
# 1: Countdown/swap (collision detected, wait for 5 seconds)
# 2: Final (game over, show results for 10 seconds)
# 3: Waiting for players (waiting screen)

def obstacle_reset():
    """
    Resets all obstacles to an inactive state and randomizes their start positions.
    """
    for obstacle in obstacles:
        obstacle.active = False
        obstacle.rnd_start()

def game_setup():
    """
    Sets up the initial game environment with obstacles.
    """
    height = 1080
    width = 1920
    obstacles = [Tree(width, height) for _ in range(20)]
    obstacles.extend([Rabbit(width, height) for _ in range(4)])
    return obstacles

def switch_player():
    """
    Switches the active player and handles the transition to run_state = 1 or run_state = 2.
    """
    global run_state
    with lock:
        for i, player in enumerate(players):
            if player.status:
                player.status = False
                player.active = False
                if i + 1 < len(players):
                    players[i + 1].status = True
                    players[i + 1].active = True
                    run_state = 1  # Set countdown state
                else:
                    run_state = 2  # No more players, final state
                print(f"[DEBUG] Switched player. New run_state: {run_state}")
                return

def handle_client(client_socket, addr):
    global game_started, run_state
    print(f"[INFO] Client connected: {addr}")

    width, height = 1920, 1080
    player_bike = Bike(width, height, client_socket, addr)

    with lock:
        players.append(player_bike)

        # Initialize players and start the game
        if len(players) == 1:
            players[0].status = True
            players[0].active = True
            print("[INFO] Waiting for second player...")
        elif len(players) == 2:
            game_started = True
            run_state = 0  # Transition to game running state
            for player in players:
                player.active = True
            print("[INFO] Both players connected. Starting game!")

    running = True
    while running:
        try:
            with lock:
                current_run_state = run_state  # Avoid race conditions

            if current_run_state == 0:
                # Normal gameplay loop
                print("[DEBUG] Game running (run_state = 0)")
                for obstacle in obstacles:
                    if not obstacle.active:
                        obstacle.activate()
                        break
                for obstacle in obstacles:
                    if obstacle.active:
                        obstacle.update()

                player_bike.update()
                player_bike.score += 0.1

                # Check for collisions
                for obstacle in obstacles:
                    if obstacle.active:
                        if (player_bike.hitbox_right > obstacle.hitbox_left and 
                            player_bike.hitbox_left < obstacle.hitbox_right and
                            player_bike.hitbox_bottom > obstacle.hitbox_top and 
                            player_bike.hitbox_top < obstacle.hitbox_bottom):
                            print("[DEBUG] Collision detected!")
                            player_bike.active = False
                            switch_player()
                            obstacle_reset()
                            break

            elif current_run_state == 1:
                # Countdown state
                print("[DEBUG] Switching players (run_state = 1)")
                time.sleep(5)
                with lock:
                    run_state = 0

            elif current_run_state == 2:
                # Final state
                print("[DEBUG] Game over (run_state = 2)")
                time.sleep(10)
                with lock:
                    game_started = False
                    run_state = 3  # Reset to waiting state
                    obstacle_reset()

            elif current_run_state == 3:
                # Waiting for players
                print("[DEBUG] Waiting for players (run_state = 3)")
                time.sleep(1 / 20)  # 20 FPS
            elif current_run_state == 0:
                # Waiting for players
                print("[DEBUG] Running (run_state = 0)")
                time.sleep(1 / 20)  # 20 FPS

            # Prepare game state for the client
            game_state = {
                "bikes": [
                    {
                        "type": bike.type,
                        "position": {"x": bike.x, "y": bike.y},
                        "score": bike.score,
                        "status": bike.status,
                        "id": bike.id,
                    }
                    for bike in players
                ],
                "obstacles": [
                    {"type": obstacle.type, "position": {"x": obstacle.x, "y": obstacle.y}}
                    for obstacle in obstacles if obstacle.active
                ],
                "run_state": current_run_state,
            }

            try:
                client_socket.sendall(json.dumps(game_state).encode("utf-8"))
            except (ConnectionResetError, BrokenPipeError):
                print(f"[ERROR] Connection lost with client: {addr}")
                #running = False

        except Exception as e:
            print(f"[ERROR] Exception in game loop: {e}")
            import traceback
            traceback.print_exc()
            #running = False

    # Cleanup after disconnection
    with lock:
        players.remove(player_bike)
    client_socket.close()
    print(f"[INFO] Client disconnected: {addr}")


def start_server(host, port):
    """
    Starts the server and listens for client connections.
    """
    global obstacles
    obstacles = game_setup()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"[INFO] Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the game server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host address")
    parser.add_argument("--port", type=int, default=38901, help="Server port")
    args = parser.parse_args()
    start_server(args.host, args.port)
