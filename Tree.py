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
        trees = [car1, car2, car3]
        self.img = random.choice(trees)
        self.active = False

        # Initialize hitbox
        self.hitbox_top = 0
        self.hitbox_bottom = 0
        self.hitbox_left = 0
        self.hitbox_right = 0
        self.get_hitbox()

    def rnd_start(self):
        if random.randint(1, 3) == 1:
            self.x = random.choice([-100, self.game_width - 200])
        else:
            self.x = random.randint(1, self.game_width - 100)
        self.y = random.randint(-1000, -200)
        print(f"Tree starting at: {self.x}, {self.y}")

    def get_position(self):
        return self.x, self.y

    def update(self):
        self.y += 17
        if self.y > self.game_height:
            self.rnd_start()
        self.get_hitbox()

    def get_hitbox(self):
        # Move the hitbox to the right and down by 25% of the image's width and height
        img_width = self.img.get_width()
        img_height = self.img.get_height()
        x_offset = 0.75 * img_width  # Shift right by 25% of image width
        y_offset = 0.65 * img_height  # Shift down by 25% of image height

        # Adjust hitbox boundaries
        self.hitbox_left = self.x + x_offset
        self.hitbox_right = self.x + img_width
        self.hitbox_top = self.y + y_offset
        self.hitbox_bottom = self.y + img_height

        # Alternatively, adjust the width and height if needed
        # self.hitbox_right = self.x + img_width - x_offset
        # self.hitbox_bottom = self.y + img_height - y_offset

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_img(self):
        return self.img

    def activate(self):
        if random.randint(0, 100) == 99:
            self.active = True
