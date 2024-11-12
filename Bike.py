import json
from images import *
from hitbox import Hitbox

class Bike:
    def __init__(self, width, height, reader, writer, addr):
        self.active = True
        self.type = "bike"
        self.img = bike
        self.x = width // 2 - 35
        self.y = height - 300
        self.body_angle = 0
        self.standard_shoulders = None
        self.reader = reader  # StreamReader for receiving data
        self.writer = writer  # StreamWriter for sending data
        self.score = 0
        self.width = width
        self.height = height
        self.client_ip = addr
        self.last_x = 0
        self.last_y = 0
        self.id = 0
        self.buffer = ""  # Buffer for partial JSON data

    async def update(self):
        mult = 5  # Movement multiplier
        try:
            # Attempt to receive data asynchronously from the client
            data = await self.reader.read(1024)
            if data:
                # Decode and append received data to buffer
                self.buffer += data.decode("utf-8")

                # Process complete JSON objects in the buffer
                while True:
                    try:
                        # Parse one JSON object from the buffer
                        parsed_data, index = json.JSONDecoder().raw_decode(self.buffer)
                        self.buffer = self.buffer[index:].lstrip()  # Remove parsed JSON object from buffer

                        # Extract movement data
                        self.id, x, y = parsed_data.get("id"), parsed_data.get("x"), parsed_data.get("y")

                        # Apply movement based on x and y values
                        self.x += int(x) * mult
                        self.y += int(y) * mult

                        # Update last known values
                        self.last_x = x
                        self.last_y = y
                    except json.JSONDecodeError:
                        # Exit loop if there's incomplete data left in the buffer
                        break
        except (ValueError, ConnectionResetError) as e:
            # On error, fallback to last known x and y values
            self.x += self.last_x * mult
            self.y += self.last_y * mult

        # Constrain the bike within screen bounds
        self.x = max(0, min(self.x, self.width - self.img.get_width()))
        self.y = max(0, min(self.y, self.height - self.img.get_height()))

        # Update hitbox based on the current position
        self.get_hitbox()

    def get_hitbox(self):
        # Calculate hitbox with bike-specific adjustments
        self.hitbox_top, self.hitbox_bottom, self.hitbox_left, self.hitbox_right = Hitbox.calculate_hitbox(
            self.img, self.x, self.y, width_adjust=0, height_adjust=0
        )

    def get_position(self):
        return self.x, self.y
