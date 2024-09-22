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

## Assumptions:
- A stable network connection between client and server will be available for data transmission.
- All team members have access to the required hardware and software.
- Gesture recognition via **MediaPipe** will be sufficiently accurate for basic game controls.

---

## Roles and Responsibilities:

### Jake Liesendahl:
- Primary developer for client-server integration and game loop optimization.
- Responsible for setting up the server and managing the game logic on the server side.

### Calvin Mickelson:
- Lead on **MediaPipe** integration for gesture controls.
- Responsible for implementing player control mechanisms and testing the multiplayer component.

---
