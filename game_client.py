#!/usr/bin/env python3

import os
import numpy as np
import socket
import pygame
import json
import time
import threading
import random
import asyncio
from pynput import keyboard
from images import *

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

# Ensure assets are loaded correctly
rabbits = [rabbit] * 4
trees = [tree] * 20
player = bike
ops = [bike] * 4
print("[DEBUG] Assets loaded.")

# Connect to the server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("129.82.45.129", 41385))  # Ensure IP and port are correct
    print("[DEBUG] Connected to server at 129.82.45.129:55205.")
    return client_socket

# Listen to the server for game state updates and render visuals
def listen_and_render(client_socket, id):
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
        r, t, o = 0, 0, 0
        for bike_info in game_state.get("bikes", []):
            bike_pos = scale_position(bike_info["position"]["x"], bike_info["position"]["y"])
            if bike_info["id"] == id:
                screen.blit(player, bike_pos)
                print(f"[DEBUG] Player bike at position: {bike_pos}")
            else:
                screen.blit(ops[o % len(ops)], bike_pos)
                o += 1
                print(f"[DEBUG] Opponent bike at position: {bike_pos}")

        # Draw obstacles from game state
        for obstacle_info in game_state.get("obstacles", []):
            pos = scale_position(obstacle_info["position"]["x"], obstacle_info["position"]["y"])
            if obstacle_info["type"] == "rabbit":
                screen.blit(rabbits[r % len(rabbits)], pos)
                r += 1
                print(f"[DEBUG] Drawn rabbit at position: {pos}")
            elif obstacle_info["type"] == "tree":
                screen.blit(trees[t % len(trees)], pos)
                t += 1
                print(f"[DEBUG] Drawn tree at position: {pos}")

        pygame.display.flip()
        pygame.time.delay(50)

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
    def __init__(self, client_socket, id):
        self.id = id
        self.running = False
        self.x = 0
        self.y = 0
        self.client_socket = client_socket
        self.keys_pressed = set()

    def start(self):
        self.running = True
        asyncio.run(self.run())

    def end(self):
        self.running = False
        self.client_socket.close()

    async def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            while self.running:
                await asyncio.sleep(0.2)
                self.update_position()
                data = json.dumps({"id": self.id, "x": self.x, "y": self.y})
                self.client_socket.send(data.encode("utf-8"))

    def on_press(self, key):
        try:
            if key.char == 'w':
                self.keys_pressed.add('up')
            elif key.char == 's':
                self.keys_pressed.add('down')
            elif key.char == 'a':
                self.keys_pressed.add('left')
            elif key.char == 'd':
                self.keys_pressed.add('right')
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key.char == 'w' and 'up' in self.keys_pressed:
                self.keys_pressed.remove('up')
            elif key.char == 's' and 'down' in self.keys_pressed:
                self.keys_pressed.remove('down')
            elif key.char == 'a' and 'left' in self.keys_pressed:
                self.keys_pressed.remove('left')
            elif key.char == 'd' and 'right' in self.keys_pressed:
                self.keys_pressed.remove('right')
        except AttributeError:
            pass

    def update_position(self):
        # Horizontal movement
        if 'left' in self.keys_pressed and 'right' in self.keys_pressed:
            self.x = 0
        elif 'left' in self.keys_pressed:
            self.x = -1
        elif 'right' in self.keys_pressed:
            self.x = 1
        else:
            self.x = 0

        # Vertical movement
        if 'up' in self.keys_pressed and 'down' in self.keys_pressed:
            self.y = 0
        elif 'up' in self.keys_pressed:
            self.y = -1
        elif 'down' in self.keys_pressed:
            self.y = 1
        else:
            self.y = 0

# Main function to initialize and run the client
def main():
    id = random.randint(1000000, 2000000)
    client_socket = connect_to_server()
    controller = Controller(client_socket, id)
    threading.Thread(target=controller.start).start()  # Run the controller in a separate thread
    listen_and_render(client_socket, id)
    controller.end()  # Stop the controller when done
    client_socket.close()
    print("[DEBUG] Client socket closed.")

if __name__ == "__main__":
    main()
