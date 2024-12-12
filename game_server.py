import os
import pygame
import json
import asyncio
import argparse
<<<<<<< Updated upstream
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
=======
import ssl
import subprocess
import os
import socket
from ipaddress import ip_address
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from datetime import datetime, timedelta, timezone

from Tree import Tree
from Rabbit import Rabbit
from Bike import Bike

# Global game variables
num_players = None  # Number of players needed to start the game
players = []  # List of connected players
obstacles = []  # List of obstacles
game_started = False
run_state = 0  # 0: Waiting for players, 1: Game running, 2: Game over, 3: First player sets num_players

def obstacle_reset():
    for obstacle in obstacles:
        obstacle.active = False
        obstacle.rnd_start()

def game_setup():
    """Initialize obstacles."""
    height = 1080
    width = 1920
    obs = [Tree(width, height) for _ in range(20)]
    obs.extend([Rabbit(width, height) for _ in range(4)])
    return obs
>>>>>>> Stashed changes

def get_server_ip():
    """Get the server's actual IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def generate_ssl_certificate(server_ip_str):
    """Generate a self-signed SSL certificate with the server's IP in the SAN."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    try:
        ip_addr = ip_address(server_ip_str)
    except ValueError:
        print(f"[ERROR] Invalid IP address: {server_ip_str}")
        return

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "MyState"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "MyCity"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MyOrganization"),
        x509.NameAttribute(NameOID.COMMON_NAME, server_ip_str),
    ])

    # Use timezone-aware current time
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(ip_addr)]),
            critical=False
        ).sign(key, hashes.SHA256()))

    with open("server.key", "wb") as f:
        f.write(key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=NoEncryption()
        ))

    with open("server.crt", "wb") as f:
        f.write(cert.public_bytes(Encoding.PEM))

<<<<<<< Updated upstream
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
=======
async def handle_client(reader, writer, lock):
    global players, num_players, run_state, obstacles
    addr = writer.get_extra_info('peername')

    width, height = 1920, 1080
    player_bike = Bike(width, height, reader, addr)

    async with lock:
        players.append((player_bike, writer))
        player_bike.id = len(players)
        print(f"[DEBUG] New player connected. Total players: {len(players)}")

        if len(players) == 1:
            run_state = 3
            try:
                msg = {"run_state": 3, "your_id": player_bike.id}
                print(f"[DEBUG] Sending to first client: {msg}")
                writer.write(json.dumps(msg).encode("utf-8") + b"\n")
                await writer.drain()

                raw_data = await reader.readuntil(b'\n')
                data = json.loads(raw_data.decode("utf-8"))
                num_players_val = data.get("num_players", 2)
                num_players = num_players_val
                print(f"[DEBUG] Number of players set to: {num_players}")

                obstacles[:] = game_setup()
                run_state = 0
            except (ConnectionResetError, json.JSONDecodeError):
                print(f"[DEBUG] Player {player_bike.id} disconnected during initial setup.")
                players.remove((player_bike, writer))
                writer.close()
                await writer.wait_closed()
                return
        else:
            msg = {"run_state": run_state, "your_id": player_bike.id}
            print(f"[DEBUG] Sending to new client: {msg}")
            writer.write(json.dumps(msg).encode("utf-8") + b"\n")
            await writer.drain()

    asyncio.create_task(player_bike.read_from_client())

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        async with lock:
            if (player_bike, writer) in players:
                players.remove((player_bike, writer))
                print(f"[DEBUG] Player {player_bike.id} disconnected. Total players: {len(players)}")
        writer.close()
        await writer.wait_closed()

async def game_loop(lock):
    global players, obstacles, run_state, game_started, num_players
    while True:
        await asyncio.sleep(0.05)

        async with lock:
            if num_players is None or len(players) < num_players:
                run_state = 0
            elif not game_started:
                run_state = 1
                game_started = True
                print("[DEBUG] Game started.")

            game_state = {
                "run_state": run_state,
                "players": [
                    {
                        "id": pb.id,
                        "position": {"x": pb.x, "y": pb.y},
                        "score": pb.score,
                        "active": pb.active,
                    }
                    for pb, _ in players
                ],
                "obstacles": [
                    {"type": obs.type, "position": {"x": obs.x, "y": obs.y}}
                    for obs in obstacles if obs.active
                ] if game_started else [],
            }
            serialized_game_state = json.dumps(game_state) + "\n"

            disconnected_players = []
            for pb, w in players:
                try:
                    w.write(serialized_game_state.encode("utf-8"))
                    await w.drain()
                except (ConnectionResetError, BrokenPipeError):
                    print(f"[DEBUG] Player {pb.id} disconnected during game state update.")
                    disconnected_players.append((pb, w))

            for dp in disconnected_players:
                players.remove(dp)
                print(f"[DEBUG] Removed player {dp[0].id}. Total players: {len(players)}")

        if run_state == 1:
            for obs in obstacles:
                if not obs.active:
                    obs.activate()
                    break
                obs.update()

            for pb, _ in players:
                if pb.active:
                    pb.score += 0.1
                for obs in obstacles:
                    if obs.active and (
                        pb.hitbox_right > obs.hitbox_left and
                        pb.hitbox_left < obs.hitbox_right and
                        pb.hitbox_bottom > obs.hitbox_top and
                        pb.hitbox_top < obs.hitbox_bottom
                    ):
                        print(f"[DEBUG] Collision detected for player {pb.id}.")
                        pb.active = False
                        if all(not p[0].active for p in players):
                            run_state = 2
                        break
        elif run_state == 2:
            print("[DEBUG] Game over. Displaying results.")
            await asyncio.sleep(10)
            run_state = 0
            game_started = False
            obstacle_reset()
            for pb, _ in players:
                pb.active = True
                pb.score = 0

async def start_server(host, port):
    lock = asyncio.Lock()
    # Create SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    server = await asyncio.start_server(lambda r, w: handle_client(r, w, lock), host, port, ssl=ssl_context)
    print(f"Server started on {host}:{port} with SSL")

    asyncio.create_task(game_loop(lock))

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game Server")
    parser.add_argument("--port", type=int, default=38902, help="Port number to run the server on")
    args = parser.parse_args()

    server_ip = get_server_ip()
    print(f"[DEBUG] Using server IP: {server_ip}")
    #generate_ssl_certificate(server_ip)  # uncomment to gnerate a new key
    asyncio.run(start_server(server_ip, args.port))
>>>>>>> Stashed changes
