import os
import socket                               # For network communication
from PySide6.QtWidgets import QApplication, QWidget  # Core PySide6 widgets
from PySide6.QtUiTools import QUiLoader  
import functions.server as server

#Get server configuration from env file
HOST = "vlbelintrocrypto.hevs.ch"
PORT = 6000
last_sent_message = "" #Initialize var to keep last sending message from the user
server_demand = [] #Initialize array to get server encoding demand

class ChatClient(QWidget):
    """
    A PySide6-based chat client that connects to a server and allows
    sending/receiving messages through a graphical interface.
    """

    def __init__(self, host=HOST, port=PORT):
        """
        Initialize the chat client with server connection details.
        
        Args:
            host (str): Server hostname or IP address
            port (int): Server port number
        """
        super(ChatClient, self).__init__()  # Initialize parent QWidget class
        loader = QUiLoader()                # Create a QUiLoader instance
        self.ui = loader.load('./src/views/ISC_GUI.ui', self)  # Load the UI design from file
        self.setWindowTitle('103.2 - Internet Secured Chat')     # Set window title
        self.ui.btnSend.clicked.connect(lambda: self.send_message())  # Connect button click to send_message method
        self.ui.btnShift.clicked.connect(self.test_shift_encoder)   # Connect shift button to test shift encoder
        self.ui.btnVigenere.clicked.connect(self.test_vigenere_encoder) # Connect vigenere button to test vigenere encoder
        self.ui.btnRSA.clicked.connect(self.test_rsa_encoder) # Connect RSA button to test RSA encoder
        self.ui.userMessage.setText("/") # Set field with '/' by default
        self.ui.userMessage.returnPressed.connect(self.send_message) # User can send message with "ENTER" key
        self.socket = socket.socket()       # Create a new socket object for server communication
        self.connect_to_server(host, port)  # Establish connection to the server

    def connect_to_server(self, host, port):
        """
        Attempt to connect to the chat server.
        
        Args:
            host (str): Server hostname or IP address
            port (int): Server port number
        """
        try:
            self.socket.connect((host, port))  # Connect to server using provided host and port
        except socket.error as e:
            print(f"Error connecting to server: {e}")  # Print error message if connection fails
            self.close()  # Close the application window
    
    def send_message(self, type="", message=""):
        """
        Send the message entered by the user to the server and prepare to receive a response.
        Args:
            type (str): Message type 's', 't', 'i' (default empty)
            message (str): Message to send (default empty)
        """
        # Set last_sent_message to global so user can update it from this function
        global last_sent_message

        type = type or self.ui.userMessage.text()[1] # If type is empty, get type from message field "/t -> t"
        message = message or self.ui.userMessage.text()[3:] # If message is empty, get message from message field starting after the third character from the field
            
        self.ui.userMessage.setText(f"/{type}") # Set user message field with last type user used 

        #If message is a string, return message
        #if not, so message is bytearray(), read byte by byte and decode message, replace empty byte by ''
        text_to_show = message if isinstance(message, str) else bytes(byte for byte in message if byte != 0).decode('utf-8', 'replace')
        self.ui.receivedMessage.append(server.construct_message_to_show("You", text_to_show))  # Display user's message in the chat area

        #Send message to server
        self.socket.send(server.isc_encode(type, message))
        last_sent_message = text_to_show # Keep last sent message

    def display_message(self):
        """Display received message in textbox"""
        global last_sent_message # Global so user can update 
        global server_demand # Global so user can update

        try:
            # Vérifier si le socket est encore valide avant de recevoir un message
            if not self.socket:
                print("Socket fermé, arrêt de la réception des messages.")
                return

            raw_message, msg_type = self.get_server_message() # Get server message and type of message
            received_message = server.decode_server_message(raw_message) # decode message to make it readable

            #Show other user message if type is t and its not my message
            if msg_type == 't' and received_message != last_sent_message:
                self.ui.receivedMessage.append(server.construct_message_to_show("User", received_message))
            #Show image
            elif msg_type == 'i':
                self.ui.receivedMessage.append(server.construct_message_to_show("Image", received_message))
            #Show server message if type is 's' and make specific task
            elif msg_type == 's':
                self.ui.receivedMessage.append(server.construct_message_to_show("Server", received_message))
                #If there is a task to do
                if("task" in last_sent_message):
                    server_demand.append(received_message)# Add server demand
                    #If there are 2 demand in array, do the specific task
                    if len(server_demand) == 2:
                        encoding_text = server.handle_server_task(last_sent_message, server_demand) #Get encoding text from specific task
                        self.send_message("s", encoding_text) # send to server
                        server_demand.clear() # Clear array so we can encode again
        
        except (socket.error, ValueError) as e:
            print(f"Erreur réception : {e}")
    
    def display_messages_loop(self):
        """
        Loop to continuously display messages from the server.
        """
        while self.socket:
            try:
                self.display_message() # Continuously receive and display message from server
            except (socket.error, ConnectionResetError):
                print("Connexion interrompue par le serveur.")
                break

    def get_server_message(self):
        """
        Get server message

        Return raw_message and message type 't', 's', 'i'
        """

        #Get message Header 
        #3 first bytes for "ISC"
        #4th byte for the message type 't', 's', 'i'
        #5th and 6th bytes for the message length
        receivedHeader = self.socket.recv(6)
        
        #Get message type (3rd byte) and decode
        msg_type = receivedHeader[3:4].decode()

        #Get message length (4th and 5th bytes) and decode
        msg_size = int.from_bytes(receivedHeader[4:6], 'big')

        #Read rest of the message by his size calculate by msg_size * 4
        raw_data = self.socket.recv(msg_size * 4)

        return (raw_data,msg_type)

    def test_shift_encoder(self):
        """ Send server message to test shift encoder automatically """
        message = "task shift encode 10"
        self.send_message("s", message)

    def test_vigenere_encoder(self):
        """ Send server message to test vigenere encoder automatically """
        message = "task vigenere encode 10"
        self.send_message("s", message)

    def test_rsa_encoder(self):
        """ Send server message to test RSA encoder automatically """
        message = "task RSA encode 10"
        self.send_message("s", message)

    def closeEvent(self, event):
        """
        Handle the window close event by properly closing the socket connection.
        
        Args:
            event: The close event object
        """
        print("Fermeture de l'application...")
        try:
            if self.socket:
                self.socket.close()  # Fermer proprement le socket
                self.socket = None  # Marquer comme fermé
        except Exception as e:
            print(f"Erreur lors de la fermeture du socket : {e}")
        
        event.accept()
