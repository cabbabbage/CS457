import struct
from images import *
from hitbox import Hitbox

class Bike:
    def __init__(self, width, height, reader, writer):
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
        self.last_x = 0
        self.last_y = 0
        self.id = 0

        # Initialize hitbox attributes
        self.hitbox_top = 0
        self.hitbox_bottom = 0
        self.hitbox_left = 0
        self.hitbox_right = 0

    async def update(self):
        mult = 5  # Movement multiplier
        try:
            # Read data asynchronously from the client
            data = await self.reader.read(12)  # Expecting exactly 12 bytes for ID, x, and y
            if len(data) == 12:
                # Unpack the data from binary format
                received_id, x, y = struct.unpack(">Iii", data)

                # Check if the received ID matches the bike's ID
                if received_id == self.id:
                    # Apply movement based on x and y values
                    self.x += int(x) * mult
                    self.y += int(y) * mult

                    # Update last known values
                    self.last_x = x
                    self.last_y = y
                    print(f"[DEBUG] Updated position: x={self.x}, y={self.y}")
                else:
                    print(f"[WARNING] ID mismatch: received {received_id}, expected {self.id}")
            else:
                print(f"[ERROR] Unexpected data length: received {len(data)} bytes")

        except (ValueError, ConnectionResetError) as e:
            # On error, fallback to last known x and y values
            print(f"[ERROR] Connection or parsing issue: {e}")
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
