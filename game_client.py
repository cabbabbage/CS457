#!/usr/bin/env python3

import os
import numpy as np
import socket
import pygame
import json
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

# Ensure assets are loaded correctly
rabbits = [rabbit] * 4
trees = [tree] * 20
player = bike
ops = [bike] * 4
print("[DEBUG] Assets loaded.")

# Connect to the server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("129.82.45.129", 45411))  # Ensure IP and port are correct
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
                data = client_socket.recv(2048)  # Increase buffer size if needed
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
    listener_thread.daemon = True
    listener_thread.start()

    while not game_over:
        # Handle pygame events for keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    controller.y = -1
                elif event.key == pygame.K_s:
                    controller.y = 1
                elif event.key == pygame.K_a:
                    controller.x = -1
                elif event.key == pygame.K_d:
                    controller.x = 1
            elif event.type == pygame.KEYUP:
                if event.key in {pygame.K_w, pygame.K_s}:
                    controller.y = 0
                if event.key in {pygame.K_a, pygame.K_d}:
                    controller.x = 0

        # Clear the screen
        screen.fill((0, 0, 0))  # Black background

        # Draw bikes from game state
        r, t, o = 0, 0, 0
        for bike_info in game_state.get("bikes", []):
            bike_pos = scale_position(bike_info["position"]["x"], bike_info["position"]["y"])
            if bike_info["id"] == id:
                screen.blit(player, bike_pos)
            else:
                screen.blit(ops[o % len(ops)], bike_pos)
                o += 1

        # Draw obstacles from game state
        for obstacle_info in game_state.get("obstacles", []):
            pos = scale_position(obstacle_info["position"]["x"], obstacle_info["position"]["y"])
            if obstacle_info["type"] == "rabbit":
                screen.blit(rabbits[r % len(rabbits)], pos)
                r += 1
            elif obstacle_info["type"] == "tree":
                screen.blit(trees[t % len(trees)], pos)
                t += 1

        # Send controller updates to server
        data = json.dumps({"id": id, "x": controller.x, "y": controller.y})
        client_socket.sendall(data.encode("utf-8"))

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
