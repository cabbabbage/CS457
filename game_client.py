import os
import pygame
import json
import asyncio
import argparse
import ssl
import hmac
import hashlib
from control import Controller
import images

# Constants for server dimensions
SERVER_WIDTH, SERVER_HEIGHT = 1920, 1080


pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
client_width, client_height = screen.get_size()
pygame.display.set_caption("Client Game Visuals")
font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

input_boxes = {
    "host": {"rect": pygame.Rect(client_width // 2 - 150, client_height // 2 - 100, 300, 50), "text": ""},
    "port": {"rect": pygame.Rect(client_width // 2 - 150, client_height // 2, 300, 50), "text": ""},
    "name": {"rect": pygame.Rect(client_width // 2 - 150, client_height // 2 + 100, 300, 50), "text": ""},
}
current_focus = "host"
close_button = pygame.Rect(client_width - 50, 10, 40, 40)

def draw_close_button():
    pygame.draw.rect(screen, (255, 0, 0), close_button)
    label = font.render("X", True, (255, 255, 255))
    screen.blit(label, (close_button.x + 10, close_button.y + 5))

def scale_position(x, y):
    return int(x * client_width / SERVER_WIDTH), int(y * client_height / SERVER_HEIGHT)


async def join_game(pre_host=None, pre_port=None):
    global input_boxes, current_focus
    submit = False
    input_boxes_no_name = {
        "host": input_boxes["host"],
        "port": input_boxes["port"]
    }
    if pre_host:
        input_boxes_no_name["host"]["text"] = pre_host
    if pre_port:
        input_boxes_no_name["port"]["text"] = str(pre_port)

    while not submit:
        screen.fill((160, 130, 110))
        prompt = font.render("Enter Server Info", True, (255, 255, 255))
        screen.blit(prompt, (client_width // 2 - 150, client_height // 2 - 200))
        draw_close_button()

        for key, box in input_boxes_no_name.items():
            pygame.draw.rect(screen, (255, 255, 255), box["rect"], 2)
            label = font.render(f"{key.capitalize()}: {box['text']}", True, (255, 255, 255))
            screen.blit(label, (box["rect"].x + 10, box["rect"].y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if close_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()
                for k, b in input_boxes_no_name.items():
                    if b["rect"].collidepoint(event.pos):
                        current_focus = k
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if all(b["text"].strip() for b in input_boxes_no_name.values()):
                        submit = True
                elif event.key == pygame.K_BACKSPACE:
                    input_boxes_no_name[current_focus]["text"] = input_boxes_no_name[current_focus]["text"][:-1]
                elif len(input_boxes_no_name[current_focus]["text"]) < 20:
                    input_boxes_no_name[current_focus]["text"] += event.unicode

    return input_boxes_no_name["host"]["text"], int(input_boxes_no_name["port"]["text"])

async def connect_to_server(host, port):
    print(f"[DEBUG] Connecting to {host}:{port} with SSL...")
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    # Make sure 'server.crt' (from the server) is copied to the client's directory
    ssl_context.load_verify_locations("server.crt")
    ssl_context.check_hostname = False

    reader, writer = await asyncio.open_connection(host, port, ssl=ssl_context)
    print("[DEBUG] Secure connection established with server.")
    return reader, writer

async def submit_num_players(writer):
    input_box = pygame.Rect(client_width // 2 - 150, client_height // 2, 300, 50)
    input_text = ""

    while True:
        screen.fill((160, 130, 110))
        prompt = font.render("Enter number of players:", True, (255, 255, 255))
        screen.blit(prompt, (client_width // 2 - 300, client_height // 2 - 50))
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        input_text_render = font.render(input_text, True, (255, 255, 255))
        screen.blit(input_text_render, (input_box.x + 10, input_box.y + 10))
        draw_close_button()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.MOUSEBUTTONDOWN and close_button.collidepoint(event.pos)):
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        num_players = int(input_text.strip())
                        writer.write(json.dumps({"num_players": num_players}).encode("utf-8") + b"\n")
                        await writer.drain()
                        print(f"[DEBUG] Number of players submitted: {num_players}")
                        return
                    except ValueError:
                        print("[ERROR] Invalid number entered.")
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif len(input_text) < 3:
                    input_text += event.unicode

async def listen_and_render(reader, writer, id, controller):
    game_over = False

    async def send_controller_input():
        while not game_over:
            x, y = controller.get_keys()
            data = json.dumps({"id": id, "x": x, "y": y})
            writer.write((data + "\n").encode("utf-8"))
            await writer.drain()
            await asyncio.sleep(0.05)

    asyncio.create_task(send_controller_input())

    while not game_over:
        try:
            data = await reader.readuntil(b'\n')
            game_state = json.loads(data.decode("utf-8"))
            run_state = game_state.get("run_state", 0)
            players = game_state.get("players", [])
            obstacles = game_state.get("obstacles", [])

            screen.fill((160, 130, 110))
            draw_close_button()

            if run_state == 0:
                label = font.render("Waiting for players...", True, (255, 255, 255))
                screen.blit(label, (client_width // 2 - 150, client_height // 2))
            elif run_state == 1:
                for player in players:
                    if player["active"]:
                        pos_x, pos_y = scale_position(player["position"]["x"], player["position"]["y"])
                        screen.blit(images.bike, (pos_x, pos_y))
                        if player["id"] == id:
                            name_label = font.render("YOU", True, (255, 0, 0))
                            screen.blit(name_label, (pos_x, pos_y - name_label.get_height()))
                            score_str = f"Score: {int(player['score'])}"
                            score_label = font.render(score_str, True, (255, 255, 255))
                            screen.blit(score_label, (10, 10))
                    if player["id"] == id and not player["active"]:
                        score_str = "YOU ARE DEAD"
                        score_label = font.render(score_str, True, (255, 0, 0))
                        label_rect = score_label.get_rect(center=(client_width // 2, client_height // 2))
                        screen.blit(score_label, label_rect)

                for obstacle in obstacles:
                    pos = scale_position(obstacle["position"]["x"], obstacle["position"]["y"])
                    if obstacle["type"] == "rabbit":
                        screen.blit(images.rabbit, pos)
                    elif obstacle["type"] == "tree":
                        screen.blit(images.tree, pos)
            elif run_state == 2:
                label = font.render("Game Over", True, (255, 0, 0))
                screen.blit(label, (client_width // 2 - 100, client_height // 2 - 100))

                scored_players = [(p["id"], p["score"]) for p in players]
                scored_players.sort(key=lambda x: x[1], reverse=True)

                top_score = scored_players[0][1]
                winners = [p for p in scored_players if p[1] == top_score]

                if len(winners) == 1:
                    winner_id = winners[0][0]
                    if winner_id == id:
                        winner_label = font.render("You Won", True, (255, 255, 0))
                    else:
                        winner_label = font.render("You Lost!", True, (255, 255, 0))
                else:
                    winner_label = font.render("It's a tie!", True, (255, 255, 0))

                screen.blit(winner_label, (client_width // 2 - 50, client_height // 2))

                start_y = client_height // 2 + 50
                for i, (pid, pscore) in enumerate(scored_players):
                    if pid == id:
                        score_str = f"YOU: {int(pscore)}"
                        score_label = font.render(score_str, True, (255, 0, 0))
                    else:
                        score_str = f"Player {pid}: {int(pscore)}"
                        score_label = font.render(score_str, True, (255, 255, 255))
                    screen.blit(score_label, (client_width // 2 - 50, start_y + i * 30))

                countdown_timer = game_state.get("countdown_timer", 10)
                countdown_label = font.render(f"New game starting in {countdown_timer}...", True, (255, 255, 255))
                screen.blit(countdown_label, (client_width // 2 - 150, client_height // 2 + 200))

            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.MOUSEBUTTONDOWN and close_button.collidepoint(event.pos)):
                    pygame.quit()
                    exit()

        except (asyncio.IncompleteReadError, json.JSONDecodeError):
            break

async def main():
    parser = argparse.ArgumentParser(description="Game Client")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()

    while True:
        host, port = await join_game(pre_host=args.host, pre_port=args.port) if args.host and args.port else await join_game()
        if not host or not port:
            continue

        try:
            reader, writer = await connect_to_server(host, port)
            initial_data_raw = await reader.readuntil(b'\n')
            initial_state = json.loads(initial_data_raw.decode("utf-8"))
            id = initial_state.get("your_id")

            if initial_state.get("run_state") == 3:
                if await submit_num_players(writer) is False:
                    writer.close()
                    await writer.wait_closed()
                    continue

            controller = Controller()
            asyncio.create_task(controller.listen_for_keys())
            await listen_and_render(reader, writer, id, controller)

            writer.close()
            await writer.wait_closed()
        except ssl.SSLError as e:
            print(f"[ERROR] SSL error: {e}")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
