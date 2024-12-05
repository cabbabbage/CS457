import json
import asyncio
from images import *
from hitbox import Hitbox

class Bike:
    def __init__(self, width, height, reader, addr = None):
        self.active = True
        self.type = "bike"
        self.img = bike
        self.x = width // 2 - 35
        self.y = height - 300
        self.body_angle = 0
        self.standard_shoulders = None
        self.reader = reader  # StreamReader for reading data
        self.client_ip = addr
        self.score = 0
        self.width = width
        self.height = height
        self.last_x = 0
        self.last_y = 0
        self.id = 0
        self.buffer = ""  # Buffer for partial JSON data
        self.status = False

        # Initialize hitbox
        self.hitbox_top = 0
        self.hitbox_bottom = 0
        self.hitbox_left = 0
        self.hitbox_right = 0
        self.get_hitbox()

    async def read_from_client(self):
        """
        Constantly reads data from the client asynchronously
        and updates the bike's position and hitbox.
        """
        mult = 15  # Movement multiplier

        while True:
            try:
                # Read data from the client using the reader's read method
                data = await self.reader.read(1024)

                if not data:
                    break  # Connection closed

                data = data.decode("utf-8")

                if data:
                    # Append received data to buffer
                    self.buffer += data

                    # Process complete JSON objects in the buffer
                    try:
                        # Parse one JSON object from the buffer
                        parsed_data, index = json.JSONDecoder().raw_decode(self.buffer)

                        # Remove parsed JSON object from buffer
                        self.buffer = self.buffer[index:].lstrip()

                        # Extract movement data
                        self.id, x, y = parsed_data.get("id"), parsed_data.get("x"), parsed_data.get("y")

                        # Only print the parsed data if either x or y is not exactly "0"
                        if not(x == 0 and y == 0):
                            print(f"[DEBUG] Parsed Data - ID: {self.id}, X: {x}, Y: {y}")

                        # Apply movement based on x and y values
                        self.x += int(x) * mult
                        self.y += int(y) * mult

                        # Update last known values
                        self.last_x = x
                        self.last_y = y

                    except json.JSONDecodeError:
                        pass  # Wait for more data to complete the JSON object

                # Ensure the position stays within bounds
                self.x = max(0, min(self.x, self.width - self.img.get_width()))
                self.y = max(0, min(self.y, self.height - self.img.get_height()))

                # Update the hitbox after modifying position
                self.get_hitbox()

            except (socket.error, ValueError) as e:
                print(f"[ERROR] Error receiving controller data from client: {e}")
                # On error, fallback to last known x and y values
                self.x += self.last_x * mult
                self.y += self.last_y * mult

                # Update hitbox to reflect fallback
                self.get_hitbox()




    def get_hitbox(self):
        """
        Updates the bike's hitbox based on its current position and image.
        """
        self.hitbox_top, self.hitbox_bottom, self.hitbox_left, self.hitbox_right = Hitbox.calculate_hitbox(
            self.img, self.x, self.y, width_adjust=0, height_adjust=0
        )

    def get_position(self):
        """
        Returns the current position of the bike.
        """
        return self.x, self.y
