from pygame.locals import *
from images import *
from hitbox import Hitbox
import random


class Rabbit:
    def __init__(self, width, height):
        self.game_height = height
        self.game_width = width
        self.type = "rabbit"
        self.rnd_start()
        self.img = rabbit
        self.active = False

    def get_position(self):
        return self.x,self.y

    def rnd_start(self):
        self.side = random.choice(["left", "right"])
        self.x = -50 if self.side == "left" else self.game_width + 50
        self.y = random.randint(-100, 100)
        print(f"Rabbit starting at: {self.x}, {self.y} (side: {self.side})")

    def update(self):
        self.y += random.randint(15, 18)
        self.x += random.randint(3, 10) if self.side == "left" else -random.randint(3, 10)
        if self.y > self.game_height:
            self.active = False
            self.rnd_start()
        self.get_hitbox()

    def get_hitbox(self):
        self.hitbox_top, self.hitbox_bottom, self.hitbox_left, self.hitbox_right = Hitbox.calculate_hitbox(
            self.img, self.x, self.y, width_adjust=0, height_adjust=-25)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_img(self):
        return self.img

    def activate(self):
        if random.randint(0,100) == 99:
            self.active = True