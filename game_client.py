import os
import pygame
import json
import asyncio
import argparse
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

# Input box dimensions and variables
input_boxes = {
    "host": {"rect": pygame.Rect(client_width // 2 - 150, client_height // 2 - 100, 300, 50), "text": ""},
    "port": {"rect": pygame.Rect(client_width // 2 - 150, client_height // 2, 300, 50), "text": ""},
    "name": {"rect": pygame.Rect(client_width // 2 - 150, client_height // 2 + 100, 300, 50), "text": ""},
}
current_focus = "host"  # Current focused input box
close_button = pygame.Rect(client_width - 50, 10, 40, 40)  # "X" button dimensions


def draw_close_button():
    """Draw the close button on the screen."""
    pygame.draw.rect(screen, (255, 0, 0), close_button)
    label = font.render("X", True, (255, 255, 255))
    screen.blit(label, (close_button.x + 10, close_button.y + 5))


def scale_position(x, y):
    return int(x * client_width / SERVER_WIDTH), int(y * client_height / SERVER_HEIGHT)


async def join_game(pre_host=None, pre_port=None):
    """UI to get IP address and port number."""
    global input_boxes, current_focus
    submit = False

    # Remove the name box from input_boxes
    input_boxes_no_name = {
        "host": input_boxes["host"],
        "port": input_boxes["port"]
    }

    # Pre-fill inputs if provided
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
                    exit()  # Exit the game entirely
                for k, b in input_boxes_no_name.items():
                    if b["rect"].collidepoint(event.pos):
                        current_focus = k
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Submit all input
                    if all(b["text"].strip() for b in input_boxes_no_name.values()):
                        submit = True
                elif event.key == pygame.K_BACKSPACE:  # Remove last character
                    input_boxes_no_name[current_focus]["text"] = input_boxes_no_name[current_focus]["text"][:-1]
                elif len(input_boxes_no_name[current_focus]["text"]) < 20:  # Max length
                    input_boxes_no_name[current_focus]["text"] += event.unicode

    return input_boxes_no_name["host"]["text"], int(input_boxes_no_name["port"]["text"])



async def connect_to_server(host, port):
    """Connect to the server and return a connected socket."""
    print(f"[DEBUG] Connecting to {host}:{port}...")
    reader, writer = await asyncio.open_connection(host, port)
    print("[DEBUG] Connected to server.")
    return reader, writer


async def submit_num_players(writer):
    """Display a UI for the first player to enter the number of players."""
    input_box = pygame.Rect(client_width // 2 - 150, client_height // 2, 300, 50)
    input_text = ""  # Initialize input text

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
                exit()  # Exit the game entirely
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Submit input
                    try:
                        num_players = int(input_text.strip())
                        writer.write(json.dumps({"num_players": num_players}).encode("utf-8") + b"\n")
                        await writer.drain()
                        print(f"[DEBUG] Number of players submitted: {num_players}")
                        return  # Exit after submission
                    except ValueError:
                        print("[ERROR] Invalid number entered.")
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif len(input_text) < 3:
                    input_text += event.unicode


async def listen_and_render(reader, writer, id, controller):
    """Listen to the server for game state updates and render visuals."""
    game_over = False

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
            data = await reader.readuntil(b'\n')
            game_state = json.loads(data.decode("utf-8"))
            run_state = game_state.get("run_state", 0)
            players = game_state.get("players", [])
            obstacles = game_state.get("obstacles", [])

            screen.fill((160, 130, 110))
            # Draw the X button here as well
            draw_close_button()

            # Render the game state based on run_state
            if run_state == 0:
                label = font.render("Waiting for players...", True, (255, 255, 255))
                screen.blit(label, (client_width // 2 - 150, client_height // 2))
            elif run_state == 1:
                for player in players:
                    if player["active"]:
                        pos_x, pos_y = scale_position(player["position"]["x"], player["position"]["y"])
                        screen.blit(images.bike, (pos_x, pos_y))
                        if player["id"] == id:
                        # Draw the bike image at the scaled coordinates


                            # Render the player's name
                            name_label = font.render("YOU", True, (255, 0, 0))

                        # Draw the name label just above the bike image
                            screen.blit(name_label, (pos_x, pos_y - name_label.get_height()))
                            score_str = f"Score: {int(player['score'])}"
                            score_label = font.render(score_str, True, (255, 255, 255))
                            screen.blit(score_label, (10, 10))
                    if  player["id"]==id and not (player["active"]):
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
                # Display "Game Over"
                label = font.render("Game Over", True, (255, 0, 0))
                screen.blit(label, (client_width // 2 - 100, client_height // 2 - 100))

                # Sort players by score descending
                scored_players = [(p["id"], p["score"]) for p in players]
                scored_players.sort(key=lambda x: x[1], reverse=True)

                # Determine the winner(s)
                top_score = scored_players[0][1]
                winners = [p for p in scored_players if p[1] == top_score]

                if len(winners) == 1:
                    # A single winner
                    winner_id = winners[0][0]
                    if winner_id == id:
                        # User is the winner
                        winner_label = font.render("You Won", True, (255, 255, 0))
                    else:
                        # Another player won
                        winner_label = font.render("You Lost!", True, (255, 255, 0))
                else:
                    # It's a tie
                    winner_label = font.render("It's a tie!", True, (255, 255, 0))

                screen.blit(winner_label, (client_width // 2 - 50, client_height // 2))

                # Display all player scores under "Game Over"
                start_y = client_height // 2 + 50
                for i, (pid, pscore) in enumerate(scored_players):
                    if pid == id:
                        # Current user's score, show "YOU" in red
                        score_str = f"YOU: {int(pscore)}"
                        score_label = font.render(score_str, True, (255, 0, 0))
                    else:
                        # Other players' scores
                        score_str = f"Player {pid}: {int(pscore)}"
                        score_label = font.render(score_str, True, (255, 255, 255))
                    screen.blit(score_label, (client_width // 2 - 50, start_y + i * 30))

                # Countdown from game_state indicating new game
                countdown_timer = game_state.get("countdown_timer", 10)  # fallback to 10 if not provided
                countdown_label = font.render(f"New game starting in {countdown_timer}...", True, (255, 255, 255))
                screen.blit(countdown_label, (client_width // 2 - 150, client_height // 2 + 200))


            pygame.display.flip()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.MOUSEBUTTONDOWN and close_button.collidepoint(event.pos)):
                    pygame.quit()
                    exit()  # Exit the game entirely

        except (asyncio.IncompleteReadError, json.JSONDecodeError):
            break


async def main():
    parser = argparse.ArgumentParser(description="Game Client")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()

    while True:
        # Attempt to join game with provided args or prompt user
        host, port = await join_game(pre_host=args.host, pre_port=args.port) if args.host and args.port else await join_game()

        if not host or not port:
            continue  # Restart if user exits via the "X" button or doesn't fill fields

        reader, writer = await connect_to_server(host, port)

        initial_data_raw = await reader.readuntil(b'\n')
        initial_state = json.loads(initial_data_raw.decode("utf-8"))
        id = initial_state.get("your_id")

        if initial_state.get("run_state") == 3:
            if await submit_num_players(writer) is False:
                # If user pressed X or quit at the num players screen
                writer.close()
                await writer.wait_closed()
                continue  # Return to join_game

        controller = Controller()
        asyncio.create_task(controller.listen_for_keys())
        await listen_and_render(reader, writer, id, controller)

        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())