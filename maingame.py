import pygame, random, time, os, sys
from pygame.locals import *
from images import *
import cv2
import numpy as np
import mediapipe as mp
import math





class Tree:
    def __init__(self):
        self.type = Tree
        self.rnd_start()
        trees = [tree2]
        self.img = random.choice(trees)
        self.active = False

        self.hitbox_top = 0
        self.hitbox_bottom = 0
        self.hitbox_left = 0
        self.hitbox_right = 0

    def rnd_start(self):
        # 1 out of 3 trees appear on the far left or far right
        if random.randint(1, 3) == 1:  # 1/3 chance
            self.x = random.choice([-100, width-200])  # Far left (-50) or far right (width + 50)
        else:
            self.x = random.randint(1, width)-100   # Random x position closer to the center
        self.y = random.randint(-1000, -200)  # Start above the screen for falling effect
        print(f"Tree starting at: {self.x}, {self.y}")



    def get_hitbox(self):
        center_x, center_y = get_center(self.img)
        center_x = center_x + self.x
        center_y = center_y + self.y
        self.hitbox_top = center_y + 20
        self.hitbox_bottom = center_y + 150
        self.hitbox_left = center_x - 30  # Adjusted for tree size
        self.hitbox_right = center_x + 30

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_img(self):
        return self.img

    def activate(self):
        self.active = True




    def update(self):
        self.y = self.y + 17
        if self.y > height:  # Fixed typo: use self.y instead of ty
            self.rnd_start()
        self.get_hitbox()

    def get_hitbox(self):
        center_x, center_y = get_center(self.img)
        center_x = center_x + self.x
        center_y = center_y + self.y
        self.hitbox_top = center_y + 20
        self.hitbox_bottom = center_y + 150
        self.hitbox_left = center_x +22  # Corrected the hitbox left to be minus
        self.hitbox_right = center_x + 52  # Hitbox right remains as is
    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    def get_img(self):
        return self.img
    def activate(self):
        self.active = True




class Rabbit:
    def __init__(self):
        self.type = "rabbit"
        self.rnd_start()
        rabbits = [rabbit]
        self.img = random.choice(rabbits)
        self.active = False

        self.hitbox_top = 0
        self.hitbox_bottom = 0
        self.hitbox_left = 0
        self.hitbox_right = 0

    def rnd_start(self):

        # Start to the left (-50) or right (width + 50) of the screen
        self.side = random.choice(["left", "right"])
        if self.side == "left":
            self.x = -50  # Start off-screen to the left
        else:
            self.x = width + 50  # Start off-screen to the right
        self.y = random.randint(-1000, 100)  # Random Y position above the screen
        print(f"Rabbit starting at: {self.x}, {self.y} (side: {self.side})")

    def update(self):
        # Move down by 10 pixels
        self.y += random.randint(15,18)
        
        # Move left or right depending on starting position
        if self.side == "left":
            self.x += random.randint(3,10)  # Move to the right
        else:
            self.x += random.randint(3,10) *-1  # Move to the left

        # If the rabbit goes past the bottom of the screen, reset its position
        if self.y > height:
            self.active = False
            self.rnd_start()


        self.get_hitbox()

    def get_hitbox(self):
        center_x, center_y = get_center(self.img)
        center_x = center_x + self.x
        center_y = center_y + self.y
        self.hitbox_top = center_y + 25
        self.hitbox_bottom = center_y + 26
        self.hitbox_left = center_x - 30  # Adjust hitbox to fit the rabbit image size
        self.hitbox_right = center_x + 30

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_img(self):
        return self.img

    def activate(self):
        self.active = True







# Required constants
x = 0
y = 0
bgcolour = (255, 255, 0)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Setting up the game screen to full screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = pygame.display.get_surface().get_size()  # Get the screen size


pygame.init()
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Road Rage!!!")

# Defining some fonts
font = pygame.font.SysFont(None, 40)
font1 = pygame.font.SysFont('monospace', 30)
font2 = pygame.font.SysFont('monospace', 25)
font3 = pygame.font.SysFont(None, 70)
font4 = pygame.font.SysFont('monospace', 40)

# Reading the stored high score from a file
read = open("highscore.txt", 'r')
topScore = float(read.readline())
read.close()

# Initializing music
pygame.mixer.init()
swish = pygame.mixer.Sound("soundfiles/swish.ogg")

# Initialize MediaPipe Pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize OpenCV video capture
cap = cv2.VideoCapture(0)  # 0 is the default camera

# Initialize obstacles list with Tree objects
obstacles = [Tree() for _ in range(20)]  # More compact creation

# Add Rabbit objects to the same list
obstacles.extend([Rabbit() for _ in range(4)])  # Corrected by using extend() instead of append()





def get_center(img):
    # Get the width and height of the image
    w, h = img.get_width(), img.get_height()
    
    # Calculate the center point
    center_x = w // 2
    center_y = h // 2
    
    # Return the center as a tuple
    return center_x, center_y



def get_body_angle(last_angle, frame):
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        return last_angle, frame

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if not results.pose_landmarks:
        print("No pose detected")
        return last_angle, frame

    mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    landmarks = results.pose_landmarks.landmark
    left_shoulder = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y])
    right_shoulder = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y])

    shoulder_length = np.linalg.norm(left_shoulder - right_shoulder)
    shoulder_vector = right_shoulder - left_shoulder

    angle_degrees = np.arctan2(shoulder_vector[1], shoulder_vector[0])

    if angle_degrees < 0:
        angle_degrees = -1 * angle_degrees - 3.14
    if angle_degrees > 0:
        angle_degrees = -1 * (angle_degrees - 3.14)

    angle_degrees = angle_degrees * 100
    
    if abs(angle_degrees) > 100:
        angle_degrees = 0


    return angle_degrees, shoulder_length



def buttons(xpos, ypos, colour, text, width, height):
    pygame.draw.rect(screen, colour, (xpos, ypos, width, height))
    msg = font.render(text, 1, (0, 0, 0))
    screen.blit(msg, (xpos + 25, ypos + 12))

def start():
    pygame.mixer.music.load("soundfiles/menumusic.mp3")
    pygame.mixer.music.play(-1)
    while True:
        screen.blit(bgimage, (0, 0))
        screen.blit(roadrage, (0, 150))
        label = font.render("Press 'Enter' or click below to start.", 1, (255, 255, 0))
        screen.blit(label, (width // 4, height // 2))
        buttons(width // 3, height - 150, (229, 158, 36), "LETS GO!!", 200, 60)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if (width // 3 < mouse[0] < (width // 3 + 200)) and (height - 150 < mouse[1] < (height - 90)):
            buttons(width // 3, height - 150, (220, 160, 220), "LETS GO!!", 200, 60)
            if click[0] == 1:
                return 1
        pygame.display.update()
        command = pygame.event.poll()
        if command.type == pygame.KEYDOWN and command.key == pygame.K_RETURN:
            return 1
        if command.type == pygame.QUIT:
            pygame.quit()
            quit()








def gameover():
    while True:
        screen.blit(bgimage, (0, 0))
        screen.blit(roadrage, (0, 150))
        label = font3.render("GAME OVER", 1, (255, 255, 0))
        screen.blit(label, (width // 4, height // 2 - 100))
        label2 = font4.render("PLAY AGAIN ???", 1, (255, 165, 0))
        screen.blit(label2, (width // 4, height // 2))
        buttons(width // 4, height // 2 + 100, (0, 150, 0), "YES", 100, 50)
        buttons(width // 2, height // 2 + 100, (150, 0, 0), "QUIT", 100, 50)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if width // 4 < mouse[0] < width // 4 + 100 and height // 2 + 100 < mouse[1] < height // 2 + 150:
            buttons(width // 4, height // 2 + 100, (220, 160, 220), "YES", 100, 50)
            if click[0] == 1:
                return 1
        if width // 2 < mouse[0] < width // 2 + 100 and height // 2 + 100 < mouse[1] < height // 2 + 150:
            buttons(width // 2, height // 2 + 100, (220, 160, 220), "QUIT", 100, 50)
            if click[0] == 1:
                pygame.quit()
                quit()
        pygame.display.update()
        command = pygame.event.poll()
        if command.type == pygame.QUIT:
            pygame.quit()
            quit()

start()

# Game loop
while True:


    bike_width = bike.get_width()
    bike_height = bike.get_height()


    a = 0
    b = 0
    FPS_change = 0
    FPS = 40
    score = 0
    running = True
    Standard_shoulders = None
    new_shoulders = None


    pygame.mixer.music.load("soundfiles/bgmusic.mp3")
    pygame.mixer.music.play(-1)
    x_position = width // 2 - 35
    Y_position = height - 300
    body_angle = 0
    


    while running:
        num = random.randint(0,200)
        if num == 50:
            for tree in obstacles:
                if not tree.active:
                    print("Tree")
                    tree.activate()
                    break
        num = random.randint(0,100)
        if num == 50:
            for rabbit in obstacles:
                if not rabbit.active and rabbit.type == "rabbit":
                    rabbit.activate()
                    break
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            print("sdfsdfsdf")
            pygame.quit()
            quit()

        screen.fill(bgcolour)
        body_angle, new_shoulders = get_body_angle(body_angle, Standard_shoulders)
        
        if Standard_shoulders is None:
            Standard_shoulders = new_shoulders
        else:
            new_y = ((((new_shoulders / Standard_shoulders) - 1.1) * -9) ** 3) - 0.2
            if new_y < -30:
                new_y = -30
            if new_y > 30:
                new_y = 30

            Y_position += new_y
            if Y_position > height-170:
                Y_position = height -170
            if Y_position < 0:
                Y_position = 0

        x_position += body_angle
        if x_position > width - 70:
            x_position = width - 70
        if x_position < 0:
            x_position = 0





        screen.blit(bike, (x_position, Y_position))

        for obstical in obstacles:
            if obstical.active:
                obstical.update()
                tx = obstical.get_x()
                ty = obstical.get_y()
                screen.blit(obstical.get_img(), (tx, ty))

                # Collision detection: Check if bike is near the tree

                # Define bike hitbox (half the size of the bike)
                bike_hitbox_width = bike_width // 2  # Half the bike's width
                bike_hitbox_height = bike_height // 2  # Half the bike's height

                # Center the hitbox on the bike
                bike_hitbox_left = x_position + (bike_width // 4)  # Shift by a quarter to center the smaller hitbox
                bike_hitbox_right = bike_hitbox_left + bike_hitbox_width
                bike_hitbox_top = Y_position + (bike_height // 4)  # Shift by a quarter to center the smaller hitbox
                bike_hitbox_bottom = bike_hitbox_top + bike_hitbox_height

                # Define obstacle hitbox
                obstical_hitbox_top = obstical.hitbox_top
                obstical_hitbox_bottom = obstical.hitbox_bottom
                obstical_hitbox_left = obstical.hitbox_left
                obstical_hitbox_right = obstical.hitbox_right

                # Draw the hitboxes
                pygame.draw.rect(screen, (255, 0, 0), (bike_hitbox_left, bike_hitbox_top, bike_hitbox_width, bike_hitbox_height), 2)  # Red box for bike hitbox
                pygame.draw.rect(screen, (0, 255, 0), (obstical_hitbox_left, obstical_hitbox_top, obstical_hitbox_right - obstical_hitbox_left, obstical_hitbox_bottom - obstical_hitbox_top), 2)  # Green box for obstacle hitbox

                # Check for overlap between the bike hitbox and the obstacle hitbox
                if (bike_hitbox_right > obstical_hitbox_left and bike_hitbox_left < obstical_hitbox_right):
                    if (bike_hitbox_bottom > obstical_hitbox_top and bike_hitbox_top < obstical_hitbox_bottom):
                        print("Collision detected!")  # Optional for debugging
                        gameover()  # Trigger game over if there's overlap







        # Score display
        score += 0.1
        score_value = font.render("Score: " + str(score), 1, (255, 153, 52))
        high_score = font.render("Top Score: " + str(topScore), 1, (255, 153, 52))
        screen.blit(score_value, (10, 10))
        screen.blit(high_score, (10, 40))

        pygame.display.update()
        FPS_change += 1
        if FPS_change % 200 == 0:
            FPS += 25
        CLOCK.tick(FPS)
        if score > topScore:
            Change = open("highscore.txt", 'w')
            Change.write(str(score))
            Change.close()
            topScore = score

    gameover()