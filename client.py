import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import os
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
HEADER = b"ISC"

message_type = "s"
last_sent_message = ""

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Fonction pour envoyer un message
def send_message():
    global last_sent_message
    msg = input_field.get()
    
    if msg:
        #Message to send with length
        completeMsg = HEADER + ord(message_type).to_bytes(1) + len(msg).to_bytes(2, 'big')

        for char in msg:
            completeMsg += ord(char).to_bytes(4, 'big')

        client.send(completeMsg)

        # Afficher le message dans l'interface
        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"<Me> {msg}\n")
        chat_box.config(state=tk.DISABLED)
        chat_box.yview(tk.END)

        input_field.delete(0, tk.END)  # Efface la zone de saisie
        last_sent_message = msg

# Fonction pour recevoir des messages en arrière-plan
def receive_messages():
    while True:
        try:
            msgheader = client.recv(6)
            
            # Extraire le type et la taille du message
            msg_type = msgheader[3:4].decode()  # 1 octet
            msg_size = int.from_bytes(msgheader[4:6], 'big')

            # Lire le message complet
            raw_data = client.recv(msg_size * 4)  # Chaque caractère prend 4 octets
            # Décoder le message
            msg = ""
            for i in range(0, len(raw_data), 4):
                char_data = raw_data[i:i+4]
                msg += char_data.decode("utf-8", errors="ignore").strip('\x00')
            
            if msg == last_sent_message:
                continue
            chat_box.config(state=tk.NORMAL)
            # Affichage en fonction du type
            if msg_type == 't':
                chat_box.insert(tk.END, f"<User> {msg}\n")
            elif msg_type == 's':
                chat_box.insert(tk.END, f"<Server> {msg}\n")
            elif msg_type == 'i':
                chat_box.insert(tk.END, f"<Image> {msg}\n")
            chat_box.config(state=tk.DISABLED)
            chat_box.yview(tk.END)
        except:
            break

# Création de l’interface graphique
root = tk.Tk()
root.title("ISC Client")

# Zone de texte pour afficher les messages reçus
chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, width=50, height=15)
chat_box.pack(padx=10, pady=10)

# Zone de saisie
input_field = tk.Entry(root, width=40)
input_field.pack(padx=10, pady=5)

# Bouton d’envoi
send_button = tk.Button(root, text="Envoyer", command=send_message)
send_button.pack(pady=5)

# Thread pour écouter les messages en arrière-plan
thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

# Lancer l’interface graphique
root.mainloop()
