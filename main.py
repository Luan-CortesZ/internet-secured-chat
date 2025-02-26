import socket
import threading
import os
import client_window
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
HEADER = b"ISC"
TYPE_MAPPING = {'User' : 't', 'Server' : 's', 'Image' : 'i'}
shift_server_demand = []

last_sent_message = ""
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Function to send message
def send_message(event=None):
    global last_sent_message
    message_type = TYPE_MAPPING[client_window.get_type_value()] #Get message type
    msg = client_window.get_input_value() #Get user value
    
    if msg:
        #Message to send with type and length
        completeMsg = HEADER + ord(message_type).to_bytes(1) + len(msg).to_bytes(2, 'big')

        #Add each message character encoded in 4 bytes
        for char in msg:
            completeMsg += ord(char).to_bytes(4, 'big')

        #Send message to server
        client.send(completeMsg)

        #Write my message sent and reset input box
        client_window.write_in_box("<Me>", msg)
        client_window.reset_field()

        #Save last sent message to prevent showing 2 times my messages
        last_sent_message = msg

#Fonction pour recevoir des messages en arrière-plan
def receive_messages():
    while True:
        try:
            #Get message Header 
            receivedHeader = client.recv(6)
            
            #Extract message type and message size
            msg_type = receivedHeader[3:4].decode()
            msg_size = int.from_bytes(receivedHeader[4:6], 'big')

            #Read all message by his sizeL
            raw_data = client.recv(msg_size * 4)

            #Decode message
            received_message = ""
            for i in range(0, len(raw_data), 4):
                char_data = raw_data[i:i+4] #Read char by char
                received_message += char_data.decode("utf-8", errors="ignore").strip('\x00') #Delete empty char
            
            #If received message is the same that my last sent message, dont read the rest of the code
            if received_message == last_sent_message:
                continue
            
            #Show prefix by message type
            if msg_type == 't':
                client_window.write_in_box("<User>", received_message)
            elif msg_type == 's':
                client_window.write_in_box("<Server>", received_message)
                if("task shift encode" in last_sent_message):
                    shift_server_demand.append(received_message)
                if(len(shift_server_demand) == 2):
                    client_window.set_input_value(shift_decoder(shift_server_demand[1], shift_server_demand[0]), send_message)
                    shift_server_demand.clear()
            elif msg_type == 'i':
                client_window.write_in_box("<Image>", received_message)
        except:
            break

def shift_decoder(text, shift):
    i=len(shift)-1
    while shift[i] != ' ':
        i-=1
    
    shift = int(shift[i+1:])
    decoded_text = ""

    for char in text:
        # Décale le caractère en s'assurant de ne pas dépasser la plage Unicode
        decoded_text += chr(ord(char) + shift)

    return decoded_text

#Thread to hear message in background
thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

client_window.show_window(send_message)