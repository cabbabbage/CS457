from pygame.locals import *
from images import *
from hitbox import Hitbox
import random

class Tree:
    def __init__(self, width, height):
        self.game_height = height
        self.game_width = width
        self.type = "tree"
        self.rnd_start()
        trees = [tree2]
        self.img = random.choice(trees)
        self.active = False

    def rnd_start(self):
        if random.randint(1, 3) == 1:
            self.x = random.choice([-100, self.game_width-200])
        else:
            self.x = random.randint(1, self.game_width) - 100
        self.y = random.randint(-1000, -200)
        print(f"Tree starting at: {self.x}, {self.y}")

    def get_position(self):
        return self.x,self.y

    def update(self):
        self.y += 17
        if self.y > self.game_height:
            self.rnd_start()
        self.get_hitbox()

    def get_hitbox(self):
        # Tree-specific hitbox adjustments
        self.hitbox_top, self.hitbox_bottom, self.hitbox_left, self.hitbox_right = Hitbox.calculate_hitbox(
            self.img, self.x, self.y, width_adjust=0, height_adjust=50)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_img(self):
        return self.img

    def activate(self):
        self.active = True