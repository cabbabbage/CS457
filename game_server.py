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
turn_count = 0  # Counts the number of turns completed


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
    global players

    width, height = 1920, 1080
    addr = writer.get_extra_info('peername')  # Get client address

    # Create a new bike for the player
    player_bike = Bike(width, height, reader, addr)

    # Start reading input from client asynchronously
    asyncio.create_task(player_bike.read_from_client())

    async with lock:
        players.append((player_bike, writer))  # Store player and writer as a tuple
        player_bike.id = len(players)
        print(f"[DEBUG] New player connected. Total players: {len(players)}")

        # Send assigned ID to client
        initial_data = {
            "your_id": player_bike.id,
        }
        serialized_initial_data = json.dumps(initial_data) + "\n"
        try:
            writer.write(serialized_initial_data.encode("utf-8"))
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError):
            pass

    try:
        # Keep the connection open
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        # Clean up when client disconnects
        async with lock:
            players = [p for p in players if p[0] != player_bike]
            print(f"[DEBUG] Player disconnected. Total players: {len(players)}")
        writer.close()
        await writer.wait_closed()


async def game_loop():
    global game_started, run_state, players, active_player_index, obstacles, turn_count

    while True:
        await asyncio.sleep(0.05)  # Game loop frequency

        async with lock:
            if len(players) >= 2 and not game_started:
                game_started = True
                run_state = 0
                active_player_index = 0
                turn_count = 0  # Reset turn count
                for player in players:
                    player[0].score = 0  # Reset scores
                players[active_player_index][0].active = True  # Activate the first player
                print("[DEBUG] Game started.")

            current_run_state = run_state

        if current_run_state == 0 and game_started:  # Normal gameplay
            # Update obstacles
            for obstacle in obstacles:
                if not obstacle.active:
                    obstacle.activate()
                    break
            for obstacle in obstacles:
                if obstacle.active:
                    obstacle.update()

            # Update active player's score
            async with lock:
                active_player = players[active_player_index][0]
                if active_player.active:
                    active_player.score += 0.1

            # Check for collision between the active player's bike and obstacles
            collision_detected = False
            for obstacle in obstacles:
                if obstacle.active and (
                    active_player.hitbox_right > obstacle.hitbox_left
                    and active_player.hitbox_left < obstacle.hitbox_right
                    and active_player.hitbox_bottom > obstacle.hitbox_top
                    and active_player.hitbox_top < obstacle.hitbox_bottom
                ):
                    async with lock:
                        run_state = 1  # Collision detected, switching state
                    print(f"[DEBUG] Collision detected between player {active_player.id} and obstacle.")
                    collision_detected = True
                    break

            if collision_detected:
                continue  # Skip sending game state to clients in this iteration

        elif current_run_state == 1:  # Switching players or ending game
            countdown_timer = 5  # Starting countdown time
            while countdown_timer > 0:
                await asyncio.sleep(1)  # Wait for 1 second
                countdown_timer -= 1

                # Send game state to clients with countdown_timer
                async with lock:
                    game_state = {
                        "active_player_id": None,  # No active player during switching
                        "bike": {},
                        "obstacles": [],
                        "scores": [
                            {"id": player[0].id, "score": player[0].score}
                            for player in players
                        ],
                        "run_state": run_state,
                        "countdown_timer": countdown_timer
                    }
                    serialized_game_state = json.dumps(game_state) + "\n"

                # Broadcast to all clients
                async with lock:
                    for _, player_writer in players:
                        try:
                            player_writer.write(serialized_game_state.encode("utf-8"))
                            await player_writer.drain()
                        except (ConnectionResetError, BrokenPipeError):
                            continue

            async with lock:
                # Deactivate current player
                players[active_player_index][0].active = False

                # Reset the obstacles
                obstacle_reset()

                turn_count += 1  # Increment turn count
                if turn_count >= len(players):  # All players have had their turn
                    run_state = 2  # Move to final state
                    print("[DEBUG] All players have completed their turns. Moving to final state.")
                else:
                    # Rotate to the next player
                    active_player_index = (active_player_index + 1) % len(players)
                    # Activate next player
                    players[active_player_index][0].active = True
                    run_state = 0  # Back to normal gameplay
                    print(f"[DEBUG] Switched to player {players[active_player_index][0].id}")

        elif current_run_state == 2:  # Final state - Display winner
            countdown_timer = 10  # Display winner for 10 seconds
            while countdown_timer > 0:
                await asyncio.sleep(1)
                countdown_timer -= 1

                # Prepare final game state with winner announcement
                async with lock:
                    # Determine the winner
                    scores = {player[0].id: player[0].score for player in players}
                    max_score = max(scores.values())
                    winners = [player_id for player_id, score in scores.items() if score == max_score]
                    if len(winners) == 1:
                        winner_id = winners[0]
                    else:
                        winner_id = None  # It's a tie

                    game_state = {
                        "active_player_id": None,
                        "bike": {},
                        "obstacles": [],
                        "scores": [
                            {"id": player[0].id, "score": player[0].score}
                            for player in players
                        ],
                        "run_state": run_state,
                        "winner_id": winner_id,
                        "countdown_timer": countdown_timer
                    }
                    serialized_game_state = json.dumps(game_state) + "\n"

                # Broadcast to all clients
                async with lock:
                    for _, player_writer in players:
                        try:
                            player_writer.write(serialized_game_state.encode("utf-8"))
                            await player_writer.drain()
                        except (ConnectionResetError, BrokenPipeError):
                            continue

            # Reset the game after displaying the winner
            async with lock:
                game_started = True  # Set to True to restart the game
                run_state = 0
                active_player_index = 0
                turn_count = 0  # Reset turn count
                for player in players:
                    player[0].score = 0  # Reset scores
                obstacle_reset()
                players[active_player_index][0].active = True  # Activate the first player
                print("[DEBUG] Game restarting.")

        # Prepare the game state
        async with lock:
            if game_started and run_state == 0:
                active_player = players[active_player_index][0]
                game_state = {
                    "active_player_id": active_player.id,
                    "bike": {
                        "type": active_player.type,
                        "position": {"x": active_player.x, "y": active_player.y},
                        "score": active_player.score,
                        "active": active_player.active,
                        "id": active_player.id,
                    },
                    "obstacles": [
                        {"type": obstacle.type, "position": {"x": obstacle.x, "y": obstacle.y}}
                        for obstacle in obstacles if obstacle.active
                    ],
                    "scores": [
                        {"id": player[0].id, "score": player[0].score}
                        for player in players
                    ],
                    "run_state": run_state,
                }
            elif run_state == 2:
                # Final state already handled in the previous block
                continue
            else:
                game_state = {
                    "active_player_id": None,
                    "bike": {},
                    "obstacles": [],
                    "scores": [
                        {"id": player[0].id, "score": player[0].score}
                        for player in players
                    ],
                    "run_state": run_state,
                }
            serialized_game_state = json.dumps(game_state) + "\n"  # Serialize once

        # Broadcast the same game state to all players
        async with lock:
            for _, player_writer in players:
                try:
                    player_writer.write(serialized_game_state.encode("utf-8"))
                    await player_writer.drain()
                except (ConnectionResetError, BrokenPipeError):
                    continue


async def start_server(host, port):
    """Start the game server."""
    global obstacles
    obstacles = game_setup()

    server = await asyncio.start_server(handle_client, host, port)
    print(f"Server started on {host}:{port}")

    # Start the game loop
    asyncio.create_task(game_loop())

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(start_server("0.0.0.0", 38902))
