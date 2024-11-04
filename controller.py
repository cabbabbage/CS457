import socket
import asyncio
import json
from pynput import keyboard

class Controller:
    def __init__(self, socket):
        self.running = False
        self.x = 0
        self.y = 0
        self.client_socket = socket
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
                data = json.dumps((self.x, self.y))
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
        x, y = 0, 0
        if 'left' in self.keys_pressed and 'right' in self.keys_pressed:
            x = 0
        elif 'left' in self.keys_pressed:
            x = -1
        elif 'right' in self.keys_pressed:
            x = 1

        # Vertical movement
        if 'up' in self.keys_pressed and 'down' in self.keys_pressed:
            y = 0
        elif 'up' in self.keys_pressed:
            y = -1
        elif 'down' in self.keys_pressed:
            y = 1

        # Update x and y
        self.x = x
        self.y = y
