# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 09:32:31 2023

@author: Jason Dank
@author: Nico Bonanno
server
"""
import socket
import threading

# Specify the server's public IP address or domain name
SERVER_IP = "10.220.89.142"
SERVER_PORT = 1234

# socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)

# List to keep track of connected clients
connected_clients = []
client_lock = threading.Lock()

def broadcast_client_count():
    with client_lock:
        count = len(connected_clients)
        for client in connected_clients:
            try:
                client.send(b"CLIENT_COUNT " + str(count).encode())
            except Exception as e:
                print(f"Error: {e}")

def handle_client(client_socket):
    with client_lock:
        connected_clients.append(client_socket)

    while True:
        try:
            data = client_socket.recv(2048)
            if not data:
                break

            # Broadcast data to all clients except sender
            for client in connected_clients:
                if client != client_socket:
                    client.send(data)
        except Exception as e:
            print(f"Error: {e}")
            break

    with client_lock:
        connected_clients.remove(client_socket)
        client_socket.close()
        # Update client count 
        broadcast_client_count()

def accept_connections():
    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"Accepted connection: {client_addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
        # Update client count for all clients whenever a new client connects
        broadcast_client_count()

print("Server listening at {}:{}".format(SERVER_IP, SERVER_PORT))
accept_connections()