import socket
import threading
import os
import client_window
import cryptography_functions
from dotenv import load_dotenv

load_dotenv() #Load environment variables

#Get server configuration from env file
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))

HEADER = b"ISC" #Message header is always starting by "ISC"
TYPE_MAPPING = {'User' : 't', 'Server' : 's', 'Image' : 'i'} #Dictionnary to map user choice and message value
shift_server_demand = [] #Array that contain shift demand
last_sent_message = "" #Keep last message sent by user

#Create client socket and connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Function to send message
def send_message(event=None):
    """
    Send message to server
    """

    global last_sent_message #Allow to change last_sent_message var
    message_type = TYPE_MAPPING[client_window.get_type_value()] #Get message type
    user_message = client_window.get_input_value() #Get user value
    
    #Verify if msg is set
    if user_message:
        #Message to send with type and length
        user_message_encoded = HEADER + ord(message_type).to_bytes(1) + len(user_message).to_bytes(2, 'big')

        #Add each message character encoded in 4 bytes
        for char in user_message:
            user_message_encoded += ord(char).to_bytes(4, 'big')

        #Send message to server
        client.send(user_message_encoded)

        #Write my message only if sent to server
        if(message_type == 's'):
            client_window.write_in_box("<Me>", user_message)
        #Reset window field
        client_window.reset_field()

        #Save last sent message
        last_sent_message = user_message

def receive_messages():
    """
    Function to receive messages sent by other user or server
    """
    while True:
        try:
            
            (raw_message,msg_type) = get_server_message() #Get server message

            received_message = decode_server_message(raw_message) #Decode server message to make it readable
            
            #Do specific code by message type
            match msg_type:
                case 't': #User message
                    client_window.write_in_box("<User>", received_message)
                case 'i': #Image message
                    client_window.write_in_box("<Image>", received_message)
                case 's': #Server message
                    client_window.write_in_box("<Server>", received_message)
                    if("task shift encode" in last_sent_message):
                        shift_server_demand.append(received_message)
                        if(len(shift_server_demand) == 2):
                            shift = int(get_server_shift(shift_server_demand[0]))
                            text_to_shift = shift_server_demand[1]
                            client_window.set_input_value(cryptography_functions.shift_encoder(text_to_shift, shift))
                            shift_server_demand.clear()
                    if("task vigenere encode" in last_sent_message):
                        shift_server_demand.append(received_message)
                        if(len(shift_server_demand) == 2):
                            shift = get_server_shift(shift_server_demand[0])
                            text_to_shift = shift_server_demand[1]
                            client_window.set_input_value(cryptography_functions.encrypt_vigenere(text_to_shift, shift))
                case _:
                    ""
        except:
            break
    
def decode_server_message(raw_message):
    """
    Decode server message set in parameter
    """
    #Decode message
    received_message = ""
    for i in range(0, len(raw_message), 4):
        char_data = raw_message[i:i+4] #Read char by char
        received_message += char_data.decode("utf-8", errors="ignore").strip('\x00') #Delete empty char
    return received_message

def get_server_message():
    """
    Get server message

    Return raw_message and message type 't', 's', 'i'
    """

    #Get message Header 
    #3 first bytes for "ISC"
    #4th byte for the message type 't', 's', 'i'
    #5th and 6th bytes for the message length
    receivedHeader = client.recv(6)
    
    #Get message type (3rd byte) and decode
    msg_type = receivedHeader[3:4].decode()

    #Get message length (4th and 5th bytes) and decode
    msg_size = int.from_bytes(receivedHeader[4:6], 'big')

    #Read rest of the message by his size calculate by msg_size * 4
    raw_data = client.recv(msg_size * 4)

    return (raw_data,msg_type)

def get_server_shift(server_shift):
    """
    Get server shift sent 
    """
    shift = ""
    i=len(server_shift)-1
    while server_shift[i] != ' ':
        i-=1
    shift = server_shift[i+1:]
    return shift

#Thread to hear message in background
thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

#Show window
client_window.show_window(send_message)