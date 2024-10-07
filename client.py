#!/usr/bin/env python3

import socket
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def start_client():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <HOST> <PORT>")
        sys.exit(1)
    
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            logging.info(f"Connecting to server at {HOST}:{PORT}")
            client_socket.connect((HOST, PORT))

            while True:
                message = input("Enter a message to send to the server (or type 'exit' to quit): ")
                if message.lower() == 'exit':
                    break
                
                client_socket.sendall(message.encode())
                data = client_socket.recv(1024)
                logging.info(f"Received from server: {data.decode()}")

    except ConnectionRefusedError:
        logging.error(f"Failed to connect to server at {HOST}:{PORT}")
    except socket.error as e:
        logging.error(f"Socket error: {e}")
    finally:
        logging.info("Client disconnected")

if __name__ == "__main__":
    start_client()
