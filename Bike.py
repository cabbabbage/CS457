import numpy as np
from hitbox import Hitbox
from pygame.locals import *
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

    # def update(self):
    #     # Get body angle and shoulder length from TCP data
    #     self.body_angle, new_shoulders = self.get_body_angle(self.body_angle, self.standard_shoulders)
    #     self.body_angle, new_shoulders = self.get_body_angle(self.body_angle, self.standard_shoulders)
    #     if self.standard_shoulders is None:
    #         self.standard_shoulders = new_shoulders
    #     else:
    #         new_y = ((((new_shoulders / self.standard_shoulders) - 1.1) * -9) ** 3) - 0.2
    #         self.y += max(min(new_y, 30), -30)
    #         self.y = max(min(self.y, self.height - 170), 0)

    #     self.x += self.body_angle
    #     self.x = max(min(self.x, self.width - 70), 0)
        
    #     self.get_hitbox()

    def update(self):
        mult = 5
        try:
            # Attempt to receive data from client
            data = self.client_socket.recv(1024).decode("utf-8")
            if data:
                # Parse shoulder vector and length from received data (expecting JSON tuple format)
                self.id, x, y = json.loads(data)
                self.x += int(x) * mult
                self.y += int(y) * mult
                self.last_x = x
                self.last_y = y
                print("yay")
        except (socket.error, json.JSONDecodeError, ValueError):
            # If any error occurs, fallback to previous values
                self.x += self.last_x * mult
                self.y += self.last_y * mult 
        self.get_hitbox()

    def get_hitbox(self):
        # Bike-specific hitbox adjustments
        self.hitbox_top, self.hitbox_bottom, self.hitbox_left, self.hitbox_right = Hitbox.calculate_hitbox(
            self.img, self.x, self.y, width_adjust=0, height_adjust=0
        )

    def get_position(self):
        return self.x, self.y
