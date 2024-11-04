import numpy as np
from hitbox import Hitbox
from images import *
import socket
import json

class Bike:
    def __init__(self, width, height, client_socket, addr):
        self.active = True
        self.type = "bike"
        self.img = bike
        self.x = width // 2 - 35
        self.y = height - 300
        self.body_angle = 0
        self.standard_shoulders = None
        self.client_socket = client_socket
        self.score = 0
        self.width = width
        self.height = height
        self.client_ip = addr
        self.last_x = 0
        self.last_y = 0
        self.id = 0

    def update(self):
        mult = 5  # Movement multiplier
        try:
            # Attempt to receive data from client
            data = self.client_socket.recv(1024).decode("utf-8")
            if data:
                # Parse the received data
                parsed_data = json.loads(data)
                self.id, x, y = parsed_data.get("id"), parsed_data.get("x"), parsed_data.get("y")

                # Apply movement based on received x and y
                self.x += int(x) * mult
                self.y += int(y) * mult

                # Store last known values
                self.last_x = x
                self.last_y = y
                print(f"[DEBUG] Updated position to ({self.x}, {self.y}) with input ({x}, {y})")
        except (socket.error, json.JSONDecodeError, ValueError) as e:
            # If an error occurs, fallback to previous values
            print(f"[ERROR] Error receiving data: {e}. Using last known values.")
            self.x += self.last_x * mult
            self.y += self.last_y * mult 

        # Ensure the bike stays within screen bounds
        self.x = max(0, min(self.x, self.width - self.img.get_width()))
        self.y = max(0, min(self.y, self.height - self.img.get_height()))

        # Update hitbox
        self.get_hitbox()

    def get_hitbox(self):
        # Bike-specific hitbox adjustments
        self.hitbox_top, self.hitbox_bottom, self.hitbox_left, self.hitbox_right = Hitbox.calculate_hitbox(
            self.img, self.x, self.y, width_adjust=0, height_adjust=0
        )

    def get_position(self):
        return self.x, self.y
