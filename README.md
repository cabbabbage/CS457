
# CS457 Multiplayer Runner Game

## Team:
- **Jake Liesendahl**
- **Calvin Mickelson**

## Project Objective:
The objective of this project is to transform a single-player runner game into a **true multiplayer experience** with a client-server architecture, robust error handling, thorough testing, and improved UI elements. Players connect to a central server that handles the game logic and streaming visuals, allowing multiple players to play simultaneously rather than taking turns.

---

## Scope:

### Inclusions:
- Refactor a local runner game into separate **client** and **server** components.
- Implement **true multiplayer** gameplay, where multiple players can connect at once, move simultaneously, and compete.
- Update the UI to provide a cleaner, more intuitive user experience.
- Emphasize **testing and error handling** to ensure a stable and reliable gaming environment.

### Exclusions:
- MediaPipe gesture controls have been removed; input now relies on more conventional controls.
- Complex AI or non-player enemies beyond basic obstacles remain out of scope.
- Cross-platform deployment beyond local or LAN play is not guaranteed.

---

## Deliverables:
- A functional multiplayer runner game that runs on a client-server model.
- Clients send player input (e.g., movement keys) to the server; the server updates the game state and sends updated visuals back.
- Improved UI and on-screen feedback (e.g., player IDs displayed above their characters).
- Thorough documentation and emphasis on testing and robust error handling.

---

## Instructions to Run the Server and Client:

### Running the Server:
1. Navigate to the directory containing `game_server.py`:
   ```bash
   cd /path/to/your/project
   ```
2. Start the server using `argparse` for the port:
   ```bash
   python game_server.py --port <SERVER_PORT>
   ```
   Replace `<SERVER_PORT>` with the desired port (e.g., `38902`).

   Example:
   ```bash
   python game_server.py --port 38902
   ```

3. The server will log messages like:
   ```
   [INFO] Server listening on 0.0.0.0:38902
   ```

### Running the Client:
1. Navigate to the directory containing `game_client.py`:
   ```bash
   cd /path/to/your/project
   ```
2. Start the client:
   ```bash
   python game_client.py --host <SERVER_HOST> --port <SERVER_PORT>
   ```
   Replace `<SERVER_HOST>` and `<SERVER_PORT>` as needed.

   Example:
   ```bash
   python game_client.py --host 127.0.0.1 --port 38902
   ```

3. The client will connect, display the updated UI, and participate in the multiplayer runner.

---

## Timeline:

### Key Milestones:
1. **Initial Game Setup**: Confirm local runner game runs with keyboard controls.
2. **Refactor to Client-Server**: Split game logic into client and server.
3. **Multiplayer Integration**: Allow multiple clients to connect and play simultaneously.
4. **UI/UX Improvements**: Display player IDs, game states, and scores clearly on-screen.
5. **Testing and Error Handling**: Rigorously test the client and server for latency, disconnects, and edge cases.

---

## Testing and Error Handling:

- Implement comprehensive error checks when clients disconnect unexpectedly or send malformed data.
- Test with multiple simultaneous clients to ensure stable performance.
- Add logging and debug messages on both client and server to trace issues.
- Run stress tests to ensure the server handles multiple players joining, leaving, and running the game for extended periods.

---

## Technical Requirements:

### Hardware:
- Local machines (clients) and a server machine (can be local or remote).
  
### Software:
- **Python** and **Pygame** for rendering and logic.
- **Asyncio** and **Sockets** for networking.
- **argparse** for flexible command-line parameter handling.
- The server and client are tested on Linux or Windows environments.

---

## Server and Client Details:

### Server:
- Listens for incoming TCP connections.
- Manages all player states, obstacle positions, and scoring.
- Regularly broadcasts the updated game state to all connected clients.

### Client:
- Connects to the server using host and port arguments.
- Sends user input (e.g., keyboard movement) to the server.
- Receives updated game state (positions, scores, winner announcements) to display in real-time.

---

## Roles and Responsibilities:

### Jake Liesendahl:
- Lead on the server architecture, error handling, and testing strategies.
- Ensures the server gracefully handles disconnects and malformed data.

### Calvin Mickelson:
- Focus on client input handling, UI improvements, and stable communication logic.
- Responsible for implementing the multiplayer visuals and verifying UI responsiveness under stress conditions.

---
