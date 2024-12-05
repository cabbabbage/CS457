
import os
import numpy as np
import socket
import json
import threading
import random
import time
from images import *
import argparse
from control import Controller  # Import the Controller class

# Constants for server dimensions
SERVER_WIDTH, SERVER_HEIGHT = 1920, 1080

# Initialize pygame based on fullscreen mode
def init_pygame(fullscreen):
    pygame.init()
    if fullscreen:
        # Fullscreen mode
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        # Windowed mode (half screen size)
        screen = pygame.display.set_mode((SERVER_WIDTH // 2, SERVER_HEIGHT // 2))
    
    client_width, client_height = screen.get_size()
    pygame.display.set_caption("Client Game Visuals")
    font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()
    return screen, client_width, client_height, font, clock

def scale_position(x, y, client_width, client_height):
    return int(x * client_width / SERVER_WIDTH), int(y * client_height / SERVER_HEIGHT)

# Ensure assets are loaded correctly
rabbits = [rabbit] * 4
trees = [tree] * 0
player = bike
ops = [bike] * 4
print("[DEBUG] Assets loaded.")

# Connect to the server
def connect_to_server():
    parser = argparse.ArgumentParser(description="Connect to the game server.")
    parser.add_argument("--host", type=str, required=True, help="Server host address")
    parser.add_argument("--port", type=int, required=True, help="Server port")
    parser.add_argument("--F", action='store_true', help="If True, run in fullscreen mode. Otherwise, windowed.")
    args = parser.parse_args()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((args.host, args.port))
    return client_socket, args.F

# Listen to the server for game state updates and render visuals
def listen_and_render(client_socket, id, controller, fullscreen, screen, client_width, client_height, font, clock):
    game_over = False
    game_state = {}
    run_state = 3  # Start in "waiting for players" state
    countdown_timer = 5  # Timer for run_state = 1

    # Thread to listen for updates from the server
    def network_listener():
        nonlocal game_over, game_state, run_state
        while not game_over:
            try:
                data = client_socket.recv(2048)  # Increase buffer size if needed
                if not data:
                    print("[DEBUG] Lost connection to server.")
                game_state = json.loads(data.decode("utf-8"))
                run_state = game_state.get("run_state", 3)  # Update run_state from server
            except socket.error as e:
                print(f"[ERROR] Error receiving data from server: {e}")
                game_over = True
                break

    # Start network listener thread
    listener_thread = threading.Thread(target=network_listener)
    listener_thread.daemon = True
    listener_thread.start()

    while not game_over:
        # Use the Controller object to get key inputs
        x, y = controller.get_keys()

        # Clear the screen and handle GUI logic only if not in testing mode
        if fullscreen:  # Only render visuals if not in testing mode (i.e., fullscreen is True)
            screen.fill((0, 0, 0))  # Black background

            # Handle run_state logic
            if run_state == 3:
                # Waiting for players
                player_count = len(game_state.get("bikes", []))
                label = font.render(f"Waiting for players {player_count}/2", True, (255, 255, 255))
                screen.blit(label, (client_width // 2 - 200, client_height // 2))

            elif run_state == 0:
                # Normal gameplay
                # Draw bikes from game state
                r, t = 0, 0
                for bike_info in game_state.get("bikes", []):
                    bike_pos = scale_position(bike_info["position"]["x"], bike_info["position"]["y"], client_width, client_height)
                    if bike_info["status"]:    
                        data = json.dumps({"id": id, "x": x, "y": y})
                        client_socket.sendall(data.encode("utf-8"))      
                    screen.blit(player, bike_pos)

                # Draw obstacles from game state
                for obstacle_info in game_state.get("obstacles", []):
                    pos = scale_position(obstacle_info["position"]["x"], obstacle_info["position"]["y"], client_width, client_height)
                    if obstacle_info["type"] == "rabbit":
                        screen.blit(rabbits[r % len(rabbits)], pos)
                        r += 1
                    elif obstacle_info["type"] == "tree":
                        screen.blit(trees[t % len(trees)], pos)
                        t += 1

            elif run_state == 1:
                # Switching players with countdown
                label = font.render(f"Switching Players... {countdown_timer}", True, (255, 255, 255))
                screen.blit(label, (client_width // 2 - 200, client_height // 2))
                countdown_timer -= 1 / 60  # Decrease timer (assuming 60 FPS)
                if countdown_timer <= 0:
                    countdown_timer = 5  # Reset timer for next time
                    run_state = 0  # Transition back to gameplay

            # Placeholder for run_state == 2
            elif run_state == 2:
                label = font.render("Final State: Results Coming Soon...", True, (255, 255, 255))
                screen.blit(label, (client_width // 2 - 200, client_height // 2))

            pygame.display.flip()
            clock.tick(60)  # Limit to 60 FPS

    listener_thread.join()
    game_over_screen(fullscreen, screen)

def game_over_screen(fullscreen, screen):
    if fullscreen:  # Only show game over screen if not in testing mode (i.e., fullscreen is True)
        screen.fill((0, 0, 0))  
        label = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(label, (client_width // 2 - 100, client_height // 2))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        print("[DEBUG] Game over screen displayed. Exiting game.")
    quit()

# Main function to initialize and run the client
def main():
    id = random.randint(1000000, 2000000)
    client_socket, fullscreen = connect_to_server()

    # Initialize pygame with fullscreen/windowed mode
    screen, client_width, client_height, font, clock = init_pygame(fullscreen)
    
    controller = Controller()
    listen_and_render(client_socket, id, controller, fullscreen, screen, client_width, client_height, font, clock)
    client_socket.close()
    print("[DEBUG] Client socket closed.")

if __name__ == "__main__":
    main()
