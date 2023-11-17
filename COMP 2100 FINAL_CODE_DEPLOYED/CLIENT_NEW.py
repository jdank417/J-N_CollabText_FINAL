# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 09:32:31 2023

@author: Jason Dank
@author: Nico Bonanno
client
"""
import tkinter as tk
from tkinter import filedialog
import socket
import threading

# Specify the server's public IP address or domain name
SERVER_IP = input("Enter Server IP: ")
SERVER_PORT = 1234

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            text = text_editor.get("1.0", tk.END)
            file.write(text)


def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            text = file.read()
            text_editor.delete("1.0", tk.END)
            text_editor.insert(tk.END, text)
        # Notify the server to open the same file
        client_socket.send(b"OPEN " + file_path.encode())

def handle_server_messages():
    while True:
        data = client_socket.recv(2048)
        if data.startswith(b"UPDATE"):
            _, text = data.split(b" ", 1)
            text_editor.delete("1.0", tk.END)
            text_editor.insert(tk.END, text.decode())
        elif data.startswith(b"CLIENT_COUNT"):
            with client_lock:
                _, count = data.split(b" ", 1)
                update_client_count_label(count.decode())

def send_text_changes(event):
    text = text_editor.get("1.0", tk.END)
    client_socket.send(b"UPDATE " + text.encode())

def update_client_count_label(count):
    label_text = f"Connected Clients: {count}"
    client_count_label.config(text=label_text)

# main window
root = tk.Tk()
root.geometry("400x400")
root.title("J&N CollabText")

# client count
client_count_frame = tk.Frame(root, bd=2, relief=tk.RIDGE)
client_count_frame.pack(fill=tk.X)
client_count_label = tk.Label(client_count_frame, text="Connected Clients: 1")
client_count_label.pack()

# vertical scrollbar
text_editor = tk.Text(root, wrap=tk.WORD, width=400, height=100)
text_editor.pack(expand=True, fill="both")
text_editor.bind("<KeyRelease>", send_text_changes)

# vertical scrollbar - text widget
text_scrollbar = tk.Scrollbar(text_editor)
text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_scrollbar.config(command=text_editor.yview)
text_editor.config(yscrollcommand=text_scrollbar.set)

# lock for synchronization
client_lock = threading.Lock()

# menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# "File" menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# thread to handle server messages
server_thread = threading.Thread(target=handle_server_messages)
server_thread.daemon = True
server_thread.start()


root.mainloop()
