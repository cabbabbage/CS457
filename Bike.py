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

import json
import socket

class Bike:
    def __init__(self, width, height, client_socket, addr):
        self.x = width // 2 - 35
        self.y = height - 300
        self.last_x = 0
        self.last_y = 0
        self.id = 0
        self.client_socket = client_socket
        self.buffer = ""  # Buffer for incomplete JSON messages

    def update(self):
        mult = 5  # Movement multiplier
        try:
            # Attempt to receive data from client
            data = self.client_socket.recv(1024).decode("utf-8")
            if data:
                # Append new data to the buffer
                self.buffer += data

                # Process complete JSON objects
                while True:
                    try:
                        # Attempt to parse JSON object from the buffer
                        parsed_data, index = json.JSONDecoder().raw_decode(self.buffer)
                        self.buffer = self.buffer[index:].lstrip()  # Remove parsed object from buffer

                        # Extract and apply movement based on x and y
                        self.id, x, y = parsed_data.get("id"), parsed_data.get("x"), parsed_data.get("y")
                        self.x += int(x) * mult
                        self.y += int(y) * mult

                        # Store last known values
                        self.last_x = x
                        self.last_y = y
                    except json.JSONDecodeError:
                        # Break if there's an incomplete JSON object remaining in the buffer
                        break
        except (socket.error, ValueError) as e:
            # If an error occurs, fallback to previous values
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
