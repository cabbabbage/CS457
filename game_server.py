import json
import asyncio
import argparse
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
