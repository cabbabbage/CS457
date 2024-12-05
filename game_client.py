import os
import numpy as np
import socket
import pygame
import json
import asyncio
import random
import time
from control import Controller
import argparse
import images

# Constants for server dimensions
SERVER_WIDTH, SERVER_HEIGHT = 1920, 1080

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
client_width, client_height = screen.get_size()
pygame.display.set_caption("Client Game Visuals")
font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()
print("[DEBUG] Full-screen mode with dimensions:", client_width, "x", client_height)

def scale_position(x, y):
    return int(x * client_width / SERVER_WIDTH), int(y * client_height / SERVER_HEIGHT)

# Calculate scaling factors for images
scale_x = client_width / SERVER_WIDTH
scale_y = client_height / SERVER_HEIGHT

# Load images
player_image = images.bike  # Assuming images.bike is a loaded pygame.Surface
tree_image = images.tree
rabbit_image = images.rabbit  # Assuming you have a rabbit image

# Scale images according to client dimensions
player_image = pygame.transform.scale(player_image, (
    int(player_image.get_width() * scale_x),
    int(player_image.get_height() * scale_y)
))

tree_image = pygame.transform.scale(tree_image, (
    int(tree_image.get_width() * scale_x),
    int(tree_image.get_height() * scale_y)
))

rabbit_image = pygame.transform.scale(rabbit_image, (
    int(rabbit_image.get_width() * scale_x),
    int(rabbit_image.get_height() * scale_y)
))

print("[DEBUG] Assets loaded and scaled.")

async def connect_to_server(host, port):
    """Connect to the server and return a connected socket."""
    reader, writer = await asyncio.open_connection(host, port)
    return reader, writer

async def listen_and_render(reader, writer, id, controller):
    """Listen to the server for game state updates and render visuals."""
    game_over = False
    run_state = 3  # Start in "waiting for players" state
    active_player_id = None  # Will be updated when data is received from the server
    countdown_timer = None  # Will be updated during switching phase
    winner_id = None  # Winner's ID

    async def send_controller_input():
        """Send controller input to the server asynchronously."""
        while not game_over:
            x, y = controller.get_keys()
            data = json.dumps({"id": id, "x": x, "y": y})
            writer.write((data + "\n").encode("utf-8"))
            await writer.drain()
            await asyncio.sleep(0.05)

    asyncio.create_task(send_controller_input())

    while not game_over:
        try:
            raw_data = await reader.readuntil(b'\n')
            game_state = json.loads(raw_data.decode("utf-8"))
            run_state = game_state.get("run_state", 3)
            active_player_id = game_state.get("active_player_id")
            countdown_timer = game_state.get("countdown_timer")
            scores_list = game_state.get("scores", [])
            winner_id = game_state.get("winner_id")

            # Process scores
            your_score = 0
            opp_score = 0
            for score_entry in scores_list:
                if score_entry["id"] == id:
                    your_score = score_entry["score"]
                else:
                    opp_score = score_entry["score"]
        except (ConnectionResetError, json.JSONDecodeError, asyncio.IncompleteReadError) as e:
            print(f"[ERROR] Error receiving or parsing data from server: {e}")
            game_over = True
            break

        # Set background color to dark yellow
        screen.fill((160, 130, 110))  # RGB values for dark yellow

        if run_state == 3:
            player_count = len(scores_list)
            label = font.render(f"Waiting for players {player_count}/2", True, (255, 255, 255))
            screen.blit(label, (client_width // 2 - 200, client_height // 2))
        elif run_state == 0:
            bike_info = game_state.get("bike", {})
            if bike_info:
                bike_pos = scale_position(bike_info["position"]["x"], bike_info["position"]["y"])
                screen.blit(player_image, bike_pos)

            for obstacle_info in game_state.get("obstacles", []):
                pos = scale_position(obstacle_info["position"]["x"], obstacle_info["position"]["y"])
                if obstacle_info["type"] == "rabbit":
                    screen.blit(rabbit_image, pos)
                elif obstacle_info["type"] == "tree":
                    screen.blit(tree_image, pos)

            if id == active_player_id:
                label = font.render("Your Turn", True, (255, 255, 255))
                screen.blit(label, (10, 10))
            else:
                label = font.render("Observing", True, (255, 255, 255))
                screen.blit(label, (10, 10))

            # Display scores
            your_score_label = font.render(f"Your score: {int(your_score)}", True, (255, 255, 255))
            screen.blit(your_score_label, (10, 50))

            opp_score_label = font.render(f"Opp's score: {int(opp_score)}", True, (255, 255, 255))
            screen.blit(opp_score_label, (10, 90))  # 40 pixels below your score

        elif run_state == 1:
            # Display the countdown timer received from the server
            if countdown_timer is not None:
                label = font.render(f"Switching Players... {int(countdown_timer)}", True, (255, 255, 255))
            else:
                label = font.render("Switching Players...", True, (255, 255, 255))
            screen.blit(label, (client_width // 2 - 200, client_height // 2))

            # Display scores
            your_score_label = font.render(f"Your score: {int(your_score)}", True, (255, 255, 255))
            screen.blit(your_score_label, (10, 50))

            opp_score_label = font.render(f"Opp's score: {int(opp_score)}", True, (255, 255, 255))
            screen.blit(opp_score_label, (10, 90))  # 40 pixels below your score

        elif run_state == 2:
            # Final state - Display winner
            if winner_id is not None:
                if winner_id == id:
                    result_text = "You Won!"
                else:
                    result_text = "You Lost!"
            else:
                result_text = "It's a Tie!"

            label = font.render(result_text, True, (255, 255, 255))
            screen.blit(label, (client_width // 2 - 100, client_height // 2))

            # Display scores
            your_score_label = font.render(f"Your score: {int(your_score)}", True, (255, 255, 255))
            screen.blit(your_score_label, (client_width // 2 - 100, client_height // 2 + 50))

            opp_score_label = font.render(f"Opp's score: {int(opp_score)}", True, (255, 255, 255))
            screen.blit(opp_score_label, (client_width // 2 - 100, client_height // 2 + 90))  # 40 pixels below your score

            if countdown_timer is not None:
                countdown_label = font.render(f"Restarting in {int(countdown_timer)}...", True, (255, 255, 255))
                screen.blit(countdown_label, (client_width // 2 - 100, client_height // 2 + 130))

        pygame.display.flip()
        clock.tick(60)

    await game_over_screen()

async def game_over_screen():
    screen.fill((139, 119, 101))  # Dark yellow background
    label = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(label, (client_width // 2 - 100, client_height // 2))
    pygame.display.update()
    await asyncio.sleep(2)
    pygame.quit()
    print("[DEBUG] Game over screen displayed. Exiting game.")

async def main():
    id = None  # Will be assigned by the server

    parser = argparse.ArgumentParser(description="Connect to the game server.")
    parser.add_argument("--host", type=str, required=True, help="Server host address")
    parser.add_argument("--port", type=int, required=True, help="Server port")
    args = parser.parse_args()

    controller = Controller()
    asyncio.create_task(controller.listen_for_keys())

    try:
        reader, writer = await connect_to_server(args.host, args.port)

        # Read assigned ID from server
        initial_data_raw = await reader.readuntil(b'\n')
        initial_data = json.loads(initial_data_raw.decode('utf-8'))
        id = initial_data.get("your_id")
        print(f"[DEBUG] Received assigned ID from server: {id}")

        await listen_and_render(reader, writer, id, controller)
    finally:
        controller.stop()
        print("[DEBUG] Client shutting down.")

if __name__ == "__main__":
    asyncio.run(main())
