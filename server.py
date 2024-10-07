#!/usr/bin/env python3

import socket
import threading
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def handle_client(conn, addr):
    logging.info(f"New connection from {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            logging.info(f"Received from {addr}: {data.decode()}")
            conn.sendall(data)  
    except ConnectionResetError:
        logging.error(f"Connection with {addr} was reset")
    finally:
        conn.close()
        logging.info(f"Connection with {addr} closed")

def start_server():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <HOST> <PORT>")
        sys.exit(1)
    
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        logging.info(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
