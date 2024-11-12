
#!/usr/bin/env python3

import os
import numpy as np
import socket
import pygame
import zlib
import struct
import threading
import random
import time
from images import *

# Constants for server dimensions
SERVER_WIDTH, SERVER_HEIGHT = 1920, 1080

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
client_width, client_height = screen.get_size()
pygame.display.set_caption("Client Game Visuals")
font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()
print("[DEBUG] Full-screen mode with dimensions:", client_width, "x", client_height)

def scale_position(x, y):
    return int(x * client_width / SERVER_WIDTH), int(y * client_height / SERVER_HEIGHT)

def is_on_screen(position):
    x, y = position
    return 0 <= x < client_width and 0 <= y < client_height

# Ensure assets are loaded correctly
rabbits = [rabbit] * 4
trees = [tree] * 20
player = bike
ops = [bike] * 4
print("[DEBUG] Assets loaded.")

# Connect to the server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('129.82.44.245', 38901))  # Ensure IP and port are correct
    return client_socket

# Listen to the server for game state updates and render visuals
def listen_and_render(client_socket, id, controller):
    game_over = False
    game_state = {}

    # Thread to listen for updates from the server
    def network_listener():
        nonlocal game_over, game_state
        while not game_over:
            try:
                data = client_socket.recv(4096)  # Increase buffer size if needed
                if not data:
                    print("[DEBUG] Lost connection to server.")
                    game_over = True
                    break

                # Decompress and deserialize the data
                decompressed_data = zlib.decompress(data)
                game_state = deserialize_game_state(decompressed_data)

            except socket.error as e:
                print(f"[ERROR] Error receiving data from server: {e}")
                game_over = True
                break

    # Start network listener thread
    listener_thread = threading.Thread(target=network_listener)
    listener_thread.daemon = True
    listener_thread.start()

    while not game_over:
        # Handle pygame events for keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                print("[DEBUG] Quit event detected. Exiting game loop.")
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    controller.y = -1
                    print("[DEBUG] W key down - moving up. Controller y:", controller.y)
                elif event.key == pygame.K_s:
                    controller.y = 1
                    print("[DEBUG] S key down - moving down. Controller y:", controller.y)
                elif event.key == pygame.K_a:
                    controller.x = -1
                    print("[DEBUG] A key down - moving left. Controller x:", controller.x)
                elif event.key == pygame.K_d:
                    controller.x = 1
                    print("[DEBUG] D key down - moving right. Controller x:", controller.x)

            elif event.type == pygame.KEYUP:
                if event.key in {pygame.K_w, pygame.K_s}:
                    controller.y = 0
                    print("[DEBUG] W or S key up - stopping vertical movement. Controller y:", controller.y)
                if event.key in {pygame.K_a, pygame.K_d}:
                    controller.x = 0
                    print("[DEBUG] A or D key up - stopping horizontal movement. Controller x:", controller.x)


        # Clear the screen for a new frame
        screen.fill((0, 0, 0))  # Black background

        # Draw bikes on screen regardless of position change
        r, t, o = 0, 0, 0
        for bike_info in game_state.get("bikes", []):
            bike_pos = scale_position(bike_info["position"]["x"], bike_info["position"]["y"])
            if bike_info["id"] == id:
                # Draw the player's bike
                screen.blit(player, bike_pos)
            else:
                # Draw opponent bikes
                screen.blit(ops[o % len(ops)], bike_pos)
                o += 1

        # Draw obstacles from game state
        for obstacle_info in game_state.get("obstacles", []):
            pos = scale_position(obstacle_info["position"]["x"], obstacle_info["position"]["y"])
            if is_on_screen(pos):
                if obstacle_info["type"] == "rabbit":
                    screen.blit(rabbits[r % len(rabbits)], pos)
                    r += 1
                elif obstacle_info["type"] == "tree":
                    screen.blit(trees[t % len(trees)], pos)
                    t += 1

        # Send controller updates to server in binary format
        controller_data = struct.pack(">Iii", id, controller.x, controller.y)
        client_socket.sendall(controller_data)

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    listener_thread.join()
    game_over_screen()

def game_over_screen():
    screen.fill((0, 0, 0))  
    label = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(label, (client_width // 2 - 100, client_height // 2))
    pygame.display.update()
    time.sleep(2)
    pygame.quit()
    print("[DEBUG] Game over screen displayed. Exiting game.")
    quit()

# Deserialize binary game state from server
def deserialize_game_state(data):
    game_state = {"bikes": [], "obstacles": []}
    offset = 0

    # Define the expected sizes for each data structure
    bike_size = struct.calcsize(">Ifii?")
    obstacle_size = struct.calcsize(">iII")

    # Deserialize bikes
    while offset + bike_size <= len(data):
        bike_id, score, x, y, status = struct.unpack_from(">Ifii?", data, offset)
        offset += bike_size
        game_state["bikes"].append({
            "id": bike_id,
            "score": score,
            "position": {"x": x, "y": y},
            "status": status
        })

    # Deserialize obstacles
    while offset + obstacle_size <= len(data):
        type_id, x, y = struct.unpack_from(">iII", data, offset)
        offset += obstacle_size
        obstacle_type = "rabbit" if type_id == 1 else "tree"
        game_state["obstacles"].append({
            "type": obstacle_type,
            "position": {"x": x, "y": y}
        })

    return game_state


class Controller:
    def __init__(self):
        self.x = 0
        self.y = 0

# Main function to initialize and run the client
def main():
    id = random.randint(1000000, 2000000)
    client_socket = connect_to_server()
    controller = Controller()
    listen_and_render(client_socket, id, controller)
    client_socket.close()
    print("[DEBUG] Client socket closed.")

if __name__ == "__main__":
    main()
