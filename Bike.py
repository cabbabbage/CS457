import numpy as np
from hitbox import Hitbox
from pygame.locals import *
from images import *

class Bike:
    def __init__(self, width, height, client_socket):
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

    def update(self):
        # Get body angle and shoulder length from TCP data
        self.body_angle, new_shoulders = self.get_body_angle(self.body_angle, self.standard_shoulders)
        
        if self.standard_shoulders is None:
            self.standard_shoulders = new_shoulders
        else:
            new_y = ((((new_shoulders / self.standard_shoulders) - 1.1) * -9) ** 3) - 0.2
            self.y += max(min(new_y, 30), -30)
            self.y = max(min(self.y, self.height - 170), 0)

        self.x += self.body_angle
        self.x = max(min(self.x, self.width - 70), 0)
        self.get_hitbox()

    def get_hitbox(self):
        # Bike-specific hitbox adjustments
        self.hitbox_top, self.hitbox_bottom, self.hitbox_left, self.hitbox_right = Hitbox.calculate_hitbox(
            self.img, self.x, self.y, width_adjust=0, height_adjust=0
        )

    def get_body_angle(self, last_angle, standard_shoulders):
        try:
            # Attempt to receive data from client
            data = self.client_socket.recv(1024).decode("utf-8")
            if data:
                # Parse shoulder vector and length from received data (expecting JSON tuple format)
                shoulder_vector, shoulder_length = json.loads(data)
                
                # Calculate the angle in degrees
                angle_degrees = np.arctan2(shoulder_vector[1], shoulder_vector[0])

                if angle_degrees < 0:
                    angle_degrees = -1 * angle_degrees - np.pi
                if angle_degrees > 0:
                    angle_degrees = -1 * (angle_degrees - np.pi)

                angle_degrees *= 100

                # Limit angle if it exceeds threshold
                if abs(angle_degrees) > 100:
                    angle_degrees = 0

                return angle_degrees, shoulder_length
        except (socket.error, json.JSONDecodeError, ValueError):
            # If any error occurs, fallback to previous values
            print("Error receiving or parsing data, using last angle and standard shoulders.")
            return last_angle, standard_shoulders

    def get_position(self):
        return self.x, self.y
