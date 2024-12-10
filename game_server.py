import json
import asyncio
from Tree import Tree
from Rabbit import Rabbit
from Bike import Bike
import argparse
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


async def handle_client(reader, writer, lock):
    global players, num_players, run_state, obstacles

    width, height = 1920, 1080
    addr = writer.get_extra_info('peername')  # Get client address

    # Create a new bike for the player
    player_bike = Bike(width, height, reader, addr)

    async with lock:
        players.append((player_bike, writer))  # Store player and writer as a tuple
        player_bike.id = len(players)
        print(f"[DEBUG] New player connected. Total players: {len(players)}")

        # If this is the first player, set run_state = 3 and request num_players
        if len(players) == 1:
            run_state = 3
            try:
                # Send run_state = 3 to the first player
                msg = {"run_state": 3, "your_id": player_bike.id}
                print(f"[DEBUG] Sending to first client: {msg}")
                writer.write(json.dumps(msg).encode("utf-8") + b"\n")
                await writer.drain()

                # Wait for the first client to provide the number of players
                raw_data = await reader.readuntil(b'\n')
                data = json.loads(raw_data.decode("utf-8"))
                num_players = data.get("num_players", 2)  # Default to 2 if not specified
                print(f"[DEBUG] Number of players set to: {num_players}")

                # Initialize obstacles after receiving num_players
                obstacles = game_setup()
                run_state = 0  # Transition to waiting for more players
            except (ConnectionResetError, json.JSONDecodeError):
                print(f"[DEBUG] Player {player_bike.id} disconnected during initial setup.")
                players.remove((player_bike, writer))
                writer.close()
                await writer.wait_closed()
                return

        # If not the first player, send current run_state (likely 0: Waiting for players)
        else:
            msg = {"run_state": run_state, "your_id": player_bike.id}
            print(f"[DEBUG] Sending to new client: {msg}")
            writer.write(json.dumps(msg).encode("utf-8") + b"\n")
            await writer.drain()

    asyncio.create_task(player_bike.read_from_client())  # Read input asynchronously

    try:
        # Keep the connection open
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        # Clean up when client disconnects
        async with lock:
            if (player_bike, writer) in players:
                players.remove((player_bike, writer))
                print(f"[DEBUG] Player {player_bike.id} disconnected. Total players: {len(players)}")
        writer.close()
        await writer.wait_closed()


async def game_loop(lock):
    global players, obstacles, run_state, game_started

    while True:
        await asyncio.sleep(0.05)  # Game loop frequency

        async with lock:
            # Wait for num_players to be set by the first client
            if num_players is None or len(players) < num_players:
                run_state = 0  # Waiting for players
            elif not game_started:
                run_state = 1  # Game running
                game_started = True
                print("[DEBUG] Game started.")

            # Broadcast game state (including run_state) to all clients
            game_state = {
                "run_state": run_state,
                "players": [
                    {
                        "id": player_bike.id,
                        "position": {"x": player_bike.x, "y": player_bike.y},
                        "score": player_bike.score,
                        "active": player_bike.active,
                    }
                    for player_bike, _ in players
                ],
                "obstacles": [
                    {"type": obstacle.type, "position": {"x": obstacle.x, "y": obstacle.y}}
                    for obstacle in obstacles if obstacle.active
                ] if game_started else [],  # Only include obstacles during the game
            }
            serialized_game_state = json.dumps(game_state) + "\n"

            # Create a list of players to remove in case of exceptions
            disconnected_players = []

            for player_bike, writer in players:
                try:
                    writer.write(serialized_game_state.encode("utf-8"))
                    await writer.drain()
                except (ConnectionResetError, BrokenPipeError):
                    print(f"[DEBUG] Player {player_bike.id} disconnected during game state update.")
                    disconnected_players.append((player_bike, writer))

            # Remove disconnected players
            for player in disconnected_players:
                players.remove(player)
                print(f"[DEBUG] Removed player {player[0].id}. Total players: {len(players)}")

        if run_state == 1:  # Game running
            # Update obstacles
            for obstacle in obstacles:
                if not obstacle.active:
                    obstacle.activate()
                    break
                obstacle.update()

            for player_bike, _ in players:
                if player_bike.active:
                    player_bike.score += 0.1  # Increment score per frame or tick

                for obstacle in obstacles:
                    if obstacle.active and (
                        player_bike.hitbox_right > obstacle.hitbox_left
                        and player_bike.hitbox_left < obstacle.hitbox_right
                        and player_bike.hitbox_bottom > obstacle.hitbox_top
                        and player_bike.hitbox_top < obstacle.hitbox_bottom
                    ):
                        print(f"[DEBUG] Collision detected for player {player_bike.id}.")
                        player_bike.active = False  # Handle collision
                        # Check if all players are inactive
                        if all(not p[0].active for p in players):
                            run_state = 2  # Game Over
                        break  # Exit obstacle loop

        elif run_state == 2:  # Game over
            print("[DEBUG] Game over. Displaying results.")
            await asyncio.sleep(10)  # Allow clients to display game over screen
            run_state = 0
            game_started = False
            obstacle_reset()

            # Reset player states
            for player_bike, _ in players:
                player_bike.active = True
                player_bike.score = 0



async def start_server(host, port):
    """Start the game server."""
    lock = asyncio.Lock()  # Create the lock inside the event loop
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, lock), host, port)
    print(f"Server started on {host}:{port}")

    # Start the game loop
    asyncio.create_task(game_loop(lock))

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Game Server")
    parser.add_argument("--port", type=int, default=38902, help="Port number to run the server on")
    args = parser.parse_args()

    asyncio.run(start_server("0.0.0.0", args.port))