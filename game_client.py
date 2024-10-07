#!/usr/bin/env python3

import os
import tensorflow as tf
import mediapipe as mp
import cv2
import numpy as np
import socket
import pygame
import json
import time
import threading
from images import *  # Import all game images like bike, tree, rabbit

# Configure TensorFlow to use GPU 0 for MediaPipe if available
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_visible_devices(gpus[0], 'GPU')
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print(f"[DEBUG] Using GPU: {gpus[0]}")
    except RuntimeError as e:
        print(f"[ERROR] TensorFlow GPU configuration error: {e}")
else:
    print("[DEBUG] No GPU detected. Running on CPU.")

# Initialize Mediapipe and Pygame
print("[DEBUG] Initializing Mediapipe and Pygame...")
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
pygame.init()
width, height = 1800, 1000
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client Game Visuals")
font = pygame.font.SysFont(None, 40)
print("[DEBUG] Screen initialized with dimensions:", width, "x", height)

# Assets
rabbits = [rabbit for _ in range(4)]
trees = [tree for _ in range(20)]
player = bike
cap = cv2.VideoCapture(0)
print("[DEBUG] Camera capture initialized.")

# Connect to the server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 5555))
    data = json.dumps((height, width))
    client_socket.sendall(data.encode("utf-8"))
    print("[DEBUG] Connected to server at localhost:5555.")
    return client_socket

# Function to send body angle and shoulder length to the server
def controller(client_socket):
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to grab frame from camera.")
        return

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if not results.pose_landmarks:
        print("[DEBUG] No pose detected in frame.")
        return

    landmarks = results.pose_landmarks.landmark
    left_shoulder = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y])
    right_shoulder = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y])

    shoulder_length = np.linalg.norm(left_shoulder - right_shoulder)
    shoulder_vector = right_shoulder - left_shoulder

    # Prepare and send data to the server
    data = json.dumps((shoulder_vector.tolist(), shoulder_length))
    client_socket.sendall(data.encode("utf-8"))
    print(f"[DEBUG] Sent control data to server: shoulder_vector={shoulder_vector}, shoulder_length={shoulder_length}")

# Setup initial UI elements
def setup_ui():
    screen.fill((255, 255, 255))
    buttons(width // 3, height - 150, (229, 158, 36), "PLAY", 200, 60)
    pygame.display.update()
    print("[DEBUG] UI setup complete. 'PLAY' button displayed.")

# Draw a button
def buttons(xpos, ypos, colour, text, width, height):
    pygame.draw.rect(screen, colour, (xpos, ypos, width, height))
    msg = font.render(text, 1, (0, 0, 0))
    screen.blit(msg, (xpos + 25, ypos + 12))

# Listen to the server for game state updates and render visuals
def listen_and_render(client_socket):
    bike_pos = (width // 2, height - 300)
    game_over = False
    score = 0
    game_state = {}  # Initialize game_state as a shared variable

    # Thread to listen for updates from the server
    def network_listener():
        nonlocal game_over, bike_pos, score, game_state
        while not game_over:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print("[DEBUG] Lost connection to server.")
                    game_over = True
                    break
                game_state = json.loads(data.decode("utf-8"))


                # Extract bike and score information from game state
                bike_pos = (game_state["bike"]["position"]["x"], game_state["bike"]["position"]["y"])
                score = game_state["bike"]["score"]
                game_over = game_state["game_over"]
            except socket.error as e:
                print(f"[ERROR] Error receiving data from server: {e}")
                game_over = True
                break

    # Thread to send control data to the server
    def network_sender():
        while not game_over:
            controller(client_socket)
            time.sleep(0.01)  # Adjust this delay if needed for frequency of sending data

    # Start both listener and sender threads
    listener_thread = threading.Thread(target=network_listener)
    sender_thread = threading.Thread(target=network_sender)
    listener_thread.start()
    sender_thread.start()

    while not game_over:
        # Handle pygame events to prevent freezing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break

        # Clear the screen and draw assets
        screen.fill((0, 0, 0))  # Black background

        # Draw bike
        screen.blit(player, bike_pos)


        # Draw rabbits and trees based on the last received game_state
        for obstacle_info in game_state.get("obstacles", []):
            pos = (obstacle_info["position"]["x"], obstacle_info["position"]["y"])
            if obstacle_info["type"] == "rabbit":
                screen.blit(rabbit, pos)
                print(f"[DEBUG] Drawn rabbit at position: {pos}")
            elif obstacle_info["type"] == "tree":
                screen.blit(tree, pos)


        # Display score
        score_text = font.render(f"Score: {int(score)}", True, (255, 255, 0))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        pygame.time.delay(25)

    # Wait for network threads to finish when the game ends
    listener_thread.join()
    sender_thread.join()
    game_over_screen()

def game_over_screen():
    screen.fill((0, 0, 0))  # Clear screen
    label = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(label, (width // 2 - 100, height // 2))
    pygame.display.update()
    time.sleep(2)
    pygame.quit()
    print("[DEBUG] Game over screen displayed. Exiting game.")
    quit()

# Main function to initialize and run the client
def main():
    client_socket = connect_to_server()
    setup_ui()
    listen_and_render(client_socket)
    client_socket.close()
    print("[DEBUG] Client socket closed.")

if __name__ == "__main__":
    main()
