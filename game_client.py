#!/usr/bin/env python3

import os
import numpy as np
import socket
import pygame
import json
import time
import threading
from images import *
from controller import Controller

# Constants for server dimensions
SERVER_WIDTH, SERVER_HEIGHT = 1920, 1080


pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
client_width, client_height = screen.get_size()
pygame.display.set_caption("Client Game Visuals")
font = pygame.font.SysFont(None, 40)
print("[DEBUG] Full-screen mode with dimensions:", client_width, "x", client_height)


def scale_position(x, y):
    return int(x * client_width / SERVER_WIDTH), int(y * client_height / SERVER_HEIGHT)

# Assets
rabbits = [rabbit for _ in range(4)]
trees = [tree for _ in range(20)]
player = bike
ops = [bike for _ in range(4)]
print("[DEBUG] Camera capture initialized.")

# Connect to the server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("129.82.45.129", 38979))
    print("[DEBUG] Connected to server at localhost:5555.")
    return client_socket

# Listen to the server for game state updates and render visuals
def listen_and_render(client_socket):
    # Retrieve client’s IP address
    client_ip = client_socket.getsockname()[0]
    game_over = False
    game_state = {}

    # Thread to listen for updates from the server
    def network_listener():
        nonlocal game_over, game_state
        while not game_over:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print("[DEBUG] Lost connection to server.")
                    game_over = True
                    break
                game_state = json.loads(data.decode("utf-8"))
            except socket.error as e:
                print(f"[ERROR] Error receiving data from server: {e}")
                game_over = True
                break

    # Start network listener thread
    listener_thread = threading.Thread(target=network_listener)
    listener_thread.start()

    while not game_over:
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break

        # Clear the screen and draw assets
        screen.fill((0, 0, 0))  # Black background

        # Draw bikes from game state
        for bike_info in game_state.get("bikes", []):
            # Scale bike position to client screen size
            bike_pos = scale_position(bike_info["position"]["x"], bike_info["position"]["y"])
            if bike_info["ip"] == client_ip:
                # This is the client's bike
                screen.blit(player, bike_pos)
                print(f"[DEBUG] Player bike at position: {bike_pos}")
            else:
                # This is the opponent's bike
                screen.blit(bike, bike_pos)
                print(f"[DEBUG] Opponent bike at position: {bike_pos}")

        # Draw obstacles from game state
        for obstacle_info in game_state.get("obstacles", []):
            # Scale obstacle position to client screen size
            pos = scale_position(obstacle_info["position"]["x"], obstacle_info["position"]["y"])
            if obstacle_info["type"] == "rabbit":
                screen.blit(rabbit, pos)
                print(f"[DEBUG] Drawn rabbit at position: {pos}")
            elif obstacle_info["type"] == "tree":
                screen.blit(tree, pos)

        # Display score (for example, the client’s own score)
        #score = next((bike["score"] for bike in game_state.get("bikes", []) if bike["ip"] == client_ip), 0)
        #score_text = font.render(f"Score: {int(score)}", True, (255, 255, 0))
        #screen.blit(score_text, (10, 10))

        pygame.display.flip()
        pygame.time.delay(25)

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

# Main function to initialize and run the client
def main():
    client_socket = connect_to_server()
    controller = Controller(socket)
    listen_and_render(client_socket)
    client_socket.close()
    print("[DEBUG] Client socket closed.")

if __name__ == "__main__":
    main()
