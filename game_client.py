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


# Placeholder images for objects
player_image = pygame.Surface((50, 50))  # Replace with actual image loading
player_image.fill((255, 0, 0))

rabbit_image = pygame.Surface((30, 30))
rabbit_image.fill((255, 255, 255))

tree_image = pygame.Surface((150, 250))
tree_image.fill((0, 255, 0))

rabbits = [rabbit_image] * 4
trees = [tree_image] * 20
player = player_image

print("[DEBUG] Assets loaded.")


async def connect_to_server(host, port):
    """Connect to the server and return a connected socket."""
    reader, writer = await asyncio.open_connection(host, port)
    return reader, writer


async def listen_and_render(reader, writer, id, controller):
    """Listen to the server for game state updates and render visuals."""
    game_over = False
    run_state = 3  # Start in "waiting for players" state
    countdown_timer = 5  # Timer for run_state = 1

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
            raw_data = await reader.readuntil(b'\n')  # Read delimited JSON
            game_state = json.loads(raw_data.decode("utf-8"))
            run_state = game_state.get("run_state", 3)
        except (ConnectionResetError, json.JSONDecodeError) as e:
            print(f"[ERROR] Error receiving or parsing data from server: {e}")
            game_over = True
            break

        # Render visuals
        screen.fill((0, 0, 0))
        if run_state == 3:
            # Waiting for players
            player_count = len(game_state.get("bikes", []))
            label = font.render(f"Waiting for players {player_count}/2", True, (255, 255, 255))
            screen.blit(label, (client_width // 2 - 200, client_height // 2))
        elif run_state == 0:
            # Gameplay
            active_player_id = game_state["active_player_id"]
            for bike_info in game_state["bikes"]:
                bike_pos = scale_position(bike_info["position"]["x"], bike_info["position"]["y"])
                bike_color = (0, 255, 0) if bike_info["id"] == active_player_id else (255, 0, 0)
                pygame.draw.rect(screen, bike_color, (*bike_pos, 50, 50))

            for obstacle_info in game_state["obstacles"]:
                pos = scale_position(obstacle_info["position"]["x"], obstacle_info["position"]["y"])
                if obstacle_info["type"] == "rabbit":
                    screen.blit(rabbit_image, pos)
                elif obstacle_info["type"] == "tree":
                    screen.blit(tree_image, pos)

        pygame.display.flip()
        clock.tick(60)



async def game_over_screen():
    screen.fill((0, 0, 0))
    label = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(label, (client_width // 2 - 100, client_height // 2))
    pygame.display.update()
    await asyncio.sleep(2)
    pygame.quit()
    print("[DEBUG] Game over screen displayed. Exiting game.")


async def main():
    id = random.randint(1000000, 2000000)

    parser = argparse.ArgumentParser(description="Connect to the game server.")
    parser.add_argument("--host", type=str, required=True, help="Server host address")
    parser.add_argument("--port", type=int, required=True, help="Server port")
    args = parser.parse_args()

    controller = Controller()
    asyncio.create_task(controller.listen_for_keys())

    try:
        reader, writer = await connect_to_server(args.host, args.port)
        await listen_and_render(reader, writer, id, controller)
    finally:
        controller.stop()
        print("[DEBUG] Client shutting down.")


if __name__ == "__main__":
    asyncio.run(main())
