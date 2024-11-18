
# CS457 Media Pipe Runner

## Team:
- **Jake Liesendahl**
- **Calvin Mickelson**

## Project Objective:
The objective of this project is to utilize **MediaPipe** to detect player controls, transmit the MediaPipe data to a server, update the game logic on the server, and return the game visuals to the user in real-time.

---

## Scope:

### Inclusions:
- Implement an open-source runner game on a local machine for single-player use.
- Update the game controls to work with **MediaPipe** for hand or body gesture input.
- Refactor the local game code into distinct **client** and **server** components:
  - The client will handle capturing MediaPipe data and sending it to the server.
  - The server will process player inputs, update the game loop, and send the updated visuals back to the client.
- Implement multiplayer functionality:
  - Allow a second player to take turns with the active player.
  - Both players will receive the same game stream from the server. The non-active player will see the same visuals, with text overlay indicating their turn.

### Exclusions:
- Real-time player-vs-player gameplay will not be included.
- Complex AI for non-player characters or opponents is out of scope.
- Cross-platform deployment beyond local machines is not required.

---

## Deliverables:
- A fully functioning open-source runner game adapted with **MediaPipe** gesture controls.
- A **client-server architecture** that supports multiplayer turn-based gameplay.
- **Documentation** detailing the installation, setup, and usage of the game.
- A final presentation or demo showcasing the implemented features.

---

## Instructions to Run the Server and Client:

### Running the Server:
1. Navigate to the directory containing `game_server.py`:
   ```bash
   cd /path/to/your/project
   ```
2. Start the server using the following command:
   ```bash
   python game_server.py --host <SERVER_HOST> --port <SERVER_PORT>
   ```
   - Replace `<SERVER_HOST>` with the desired host (e.g., `0.0.0.0` to listen on all interfaces).
   - Replace `<SERVER_PORT>` with the desired port (e.g., `38901`).

   Example:
   ```bash
   python game_server.py --host 0.0.0.0 --port 38901
   ```

3. The server will log messages indicating its status, such as:
   ```
   [INFO] Server listening on 0.0.0.0:38901
   ```

### Running the Client:
1. Navigate to the directory containing `game_client.py`:
   ```bash
   cd /path/to/your/project
   ```
2. Start the client using the following command:
   ```bash
   python game_client.py --host <SERVER_HOST> --port <SERVER_PORT>
   ```
   - Replace `<SERVER_HOST>` with the server's IP address.
   - Replace `<SERVER_PORT>` with the server's port.

   Example:
   ```bash
   python game_client.py --host 127.0.0.1 --port 38901
   ```

3. The client will connect to the server and begin processing game visuals and controls.

---

## Timeline:

### Key Milestones:
1. **Game Setup & Single-Player Implementation**: Week 1
   - Get the open-source runner game running locally with keyboard controls.
   
2. **MediaPipe Integration for Controls**: Week 2-3
   - Replace keyboard controls with MediaPipe-based gesture controls.
   
3. **Client-Server Architecture**: Week 4-5
   - Split the game into client-server architecture and ensure smooth data transmission.
   
4. **Multiplayer Turn-based Functionality**: Week 6-7
   - Add second player functionality, allowing for turn-based gameplay.
   
5. **Testing & Optimization**: Week 8
   - Test the game for performance and latency, especially around MediaPipe data transmission.

---

## Task Breakdown:

1. **Game Setup (5 hours)**:
   - Download and configure the open-source runner game.

2. **MediaPipe Control Integration (15 hours)**:
   - Set up MediaPipe for hand/pose detection and map it to game actions.

3. **Client-Server Refactor (20 hours)**:
   - Refactor the game code to separate client and server responsibilities.

4. **Multiplayer Logic (15 hours)**:
   - Add functionality for the second player and handle turn-taking.

5. **Testing and Debugging (10 hours)**:
   - Thoroughly test for bugs, synchronization issues, and latency.

---

## Technical Requirements:

### Hardware:
- Local machines for development (clients).
- A server to handle game logic and data processing (can be a local machine).

### Software:
- Programming languages: **Python**.
- Libraries: **MediaPipe**, **Socket** for networking, **Threading** for concurrency.
- Game engine: Depends on the chosen open-source runner game (e.g., **Pygame**).
- Operating System: **Linux** or **Windows** (cross-platform support ideal but not required).

---

## Server and Client Implementation:

### Server:
1. **Socket Creation**:
   - The server uses a TCP socket to listen for incoming client connections.
2. **Handling Client Connections**:
   - A new thread is spawned for each client, using the `handle_client` method.
3. **Game State Communication**:
   - The server prepares the game state as a JSON object and sends it to the client.

### Client:
1. **Socket Creation**:
   - The client connects to the server using the specified host and port.
2. **User Interaction**:
   - The client processes MediaPipe input for player controls.
   - The user interacts with the game via gesture controls, which are transmitted to the server.

---

## Roles and Responsibilities:

### Jake Liesendahl:
- Primary developer for client-server integration and game loop optimization.
- Responsible for setting up the server and managing the game logic on the server side.

### Calvin Mickelson:
- Lead on **MediaPipe** integration for gesture controls.
- Responsible for implementing player control mechanisms and testing the multiplayer component.

---
