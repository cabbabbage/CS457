import json
import asyncio
from Tree import Tree
from Rabbit import Rabbit
from Bike import Bike

players = []
obstacles = []
game_started = False
lock = asyncio.Lock()
run_state = 3  # Default to waiting for players
active_player_index = 0  # Tracks the current active player


def obstacle_reset():
    """Reset all obstacles."""
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


async def handle_client(reader, writer):
    global game_started, run_state, players, active_player_index

    width, height = 1920, 1080
    addr = writer.get_extra_info('peername')  # Get client address

    # Create a new bike for the player
    player_bike = Bike(width, height, reader, addr)

    async with lock:
        players.append((player_bike, writer))  # Store player and writer as a tuple
        print(f"[DEBUG] New player connected. Total players: {len(players)}")

        # Check if minimum players are reached to start the game
        if len(players) >= 2 and not game_started:
            game_started = True
            run_state = 0
            active_player_index = 0
            players[active_player_index][0].active = True  # Activate the first player

    try:
        while True:
            await asyncio.sleep(0.05)  # Game loop frequency

            async with lock:
                current_run_state = run_state

            if current_run_state == 0:  # Normal gameplay
                # Update obstacles
                for obstacle in obstacles:
                    if not obstacle.active:
                        obstacle.activate()
                        break
                for obstacle in obstacles:
                    if obstacle.active:
                        obstacle.update()

                # Update active player's score
                active_player = players[active_player_index][0]
                if active_player.active:
                    active_player.score += 0.1

                # Check for collision between the active player's bike and obstacles
                for obstacle in obstacles:
                    if obstacle.active and (
                        active_player.hitbox_right > obstacle.hitbox_left
                        and active_player.hitbox_left < obstacle.hitbox_right
                        and active_player.hitbox_bottom > obstacle.hitbox_top
                        and active_player.hitbox_top < obstacle.hitbox_bottom
                    ):
                        run_state = 1  # Collision detected, switching state
                        break

            elif current_run_state == 1:  # Switching players
                await asyncio.sleep(5)  # Countdown for switching
                async with lock:
                    # Rotate to the next player
                    players[active_player_index][0].active = False  # Deactivate current player
                    active_player_index = (active_player_index + 1) % len(players)
                    players[active_player_index][0].active = True  # Activate next player
                    run_state = 0  # Back to normal gameplay

            elif current_run_state == 2:  # Game Over
                await asyncio.sleep(10)
                async with lock:
                    game_started = False
                    run_state = 3
                    obstacle_reset()

            elif current_run_state == 3:  # Waiting for players
                if len(players) >= 2:
                    game_started = True
                    run_state = 0
                    active_player_index = 0
                    players[active_player_index][0].active = True  # Activate the first player

            # Prepare the game state
            async with lock:
                game_state = {
                    "active_player_id": players[active_player_index][0].id,
                    "bikes": [
                        {
                            "type": bike.type,
                            "position": {"x": bike.x, "y": bike.y},
                            "score": bike.score,
                            "active": bike.active,
                            "id": bike.id,
                        }
                        for bike, _ in players
                    ],
                    "obstacles": [
                        {"type": obstacle.type, "position": {"x": obstacle.x, "y": obstacle.y}}
                        for obstacle in obstacles if obstacle.active
                    ],
                    "run_state": current_run_state,
                }
                serialized_game_state = json.dumps(game_state) + "\n"  # Serialize once

            # Broadcast the same game state to all players
            for _, player_writer in players:
                try:
                    player_writer.write(serialized_game_state.encode("utf-8"))
                    await player_writer.drain()
                except (ConnectionResetError, BrokenPipeError):
                    continue

    finally:
        # Clean up when client disconnects
        async with lock:
            players = [p for p in players if p[0] != player_bike]
            if not players:
                game_started = False  # Reset game if no players remain
        writer.close()
        await writer.wait_closed()


async def start_server(host, port):
    """Start the game server."""
    global obstacles
    obstacles = game_setup()

    server = await asyncio.start_server(handle_client, host, port)
    print(f"Server started on {host}:{port}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(start_server("0.0.0.0", 38902))
