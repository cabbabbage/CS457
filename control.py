# control.py
import pygame
import asyncio

class Controller:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.running = True

    async def listen_for_keys(self):
        """Continuously listens for key presses and updates direction."""
        while self.running:
            await asyncio.sleep(0.01)  # Small delay to allow for async operations
            pygame.event.pump()  # Process pygame events
            keys = pygame.key.get_pressed()  # Get all currently pressed keys
            
            if keys[pygame.K_w]:
                self.y = -1
            elif keys[pygame.K_s]:
                self.y = 1
            else:
                self.y = 0

            if keys[pygame.K_a]:
                self.x = -1
            elif keys[pygame.K_d]:
                self.x = 1
            else:
                self.x = 0

    def get_keys(self):
        """Returns the current movement direction."""
        return self.x, self.y

    def stop(self):
        """Stops the controller."""
        self.running = False
