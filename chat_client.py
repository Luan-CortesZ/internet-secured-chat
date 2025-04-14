import math
import os
import random
import socket                               # For network communication
from PySide6.QtWidgets import QApplication, QWidget  # Core PySide6 widgets
from PySide6.QtUiTools import QUiLoader  
from functions import cryptography
from PySide6.QtCore import QFile
import functions.server as server

#Get server configuration from env file
HOST = "vlbelintrocrypto.hevs.ch"
PORT = 6000
last_sent_message = "" #Initialize var to keep last sending message from the user
server_demand = [] #Initialize array to get server encoding demand
get_message = True
auto_test = False

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
        """"
        base_path = os.path.dirname(os.path.abspath(__file__))
        ui_file_path = os.path.join(base_path, 'src/views/ISC_GUI.ui')
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QFile.ReadOnly):
         print(f"Cannot open {ui_file_path}: {ui_file.errorString()}")
         self.socket = None  # Initialize socket to None explicitly to avoid AttributeError
         return
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        if not self.ui:
         print(loader.errorString())
         self.socket = None  # Again, initialize socket explicitly
         return
        """
        self.ui = loader.load('./src/views/ISC_GUI.ui', self)  # Load the UI design from file
        self.setWindowTitle('103.2 - Internet Secured Chat')     # Set window title
        self.ui.btnSend.clicked.connect(lambda: self.send_message())  # Connect button click to send_message method
        self.ui.btnShift.clicked.connect(self.test_shift_encoder)   # Connect shift button to test shift encoder
        self.ui.btnVigenere.clicked.connect(self.test_vigenere_encoder) # Connect vigenere button to test vigenere encoder
        self.ui.btnRSA.clicked.connect(self.test_rsa_encoder) # Connect RSA button to test RSA encoder
        self.ui.btnHashHash.clicked.connect(self.test_hash_hash) # Connect Hash Hash button to test Hash 
        self.ui.btnHashVerify.clicked.connect(self.test_hash_verify) # Connect Hash Verify button to test Hash verification 
        self.ui.btnDH.clicked.connect(self.test_diffie_hellman) # Connect DH button to test Diffie-Hellman
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
        global get_message
        get_message = False

        type = type or self.ui.userMessage.text()[1] # If type is empty, get type from message field "/t -> t"
        message = message or self.ui.userMessage.text()[3:] # If message is empty, get message from message field starting after the third character from the field
            
        self.ui.userMessage.setText(f"/{type}") # Set user message field with last type user used 

        #If message is a string, return message
        #if not, so message is bytearray(), read byte by byte and decode message, replace empty byte by ''
        text_to_show = message if isinstance(message, str) else bytes(byte for byte in message if byte != 0).decode('utf-8', 'replace')
        self.ui.receivedMessage.append(server.construct_message_to_show("You", text_to_show))  # Display user's message in the chat area

        #Send message to server
        self.socket.sendall(server.isc_encode(type, message))
        last_sent_message = text_to_show # Keep last sent message
        get_message = True

    def display_message(self):
        """Display received message in textbox"""
        global last_sent_message # Global so user can update 
        global auto_test

        try:
            # Vérifier si le socket est encore valide avant de recevoir un message
            if not self.socket:
                print("Socket fermé, arrêt de la réception des messages.")
                return

            raw_message, msg_type = self.get_server_message() # Get server message and type of message
            received_message = server.decode_server_message(raw_message) # decode message to make it readable

            #Show other user message if type is t and its not my message
            if msg_type == 't' and received_message != last_sent_message:
                #self.ui.receivedMessage.append(server.construct_message_to_show("User", received_message))
                print("")
            #Show image
            elif msg_type == 'i':
                ""
            #Show server message if type is 's' and make specific task
            elif msg_type == 's':
                self.ui.receivedMessage.append(server.construct_message_to_show("Server", received_message))
                if auto_test: 
                    self.test_server_demand(received_message)
                    auto_test = False
        
        except (socket.error, ValueError) as e:
            print(f"Erreur réception : {e}")
    
    def display_messages_loop(self):
        """
        Loop to continuously display messages from the server.
        """
        global get_message # Global so user can update

        while self.socket and get_message:
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

    def test_server_demand(self, received_message):
        #If there is a task to do
        global get_message
        global server_demand # Global so user can update

        get_message = False
        myNumber = int(random.randint(2,50))


        if("DifHel" in last_sent_message):
            modulo, generator = cryptography.get_diffie_hellman_prime()
            sendNumber = int(pow(generator, myNumber, modulo))
            self.send_message("s", str(modulo) + "," + str(generator)) # send to server
            server_demand += self.get_n_server_message(2)
            self.send_message("s", str(sendNumber))
            exchange_key = cryptography.get_exchange_key(int(server_demand[1]), myNumber, modulo)
            server_demand += self.get_n_server_message(1)
            self.send_message("s", str(exchange_key))
        elif("task" in last_sent_message):
            if len(last_sent_message.split()) > 2:
                n_server_message = 2 if last_sent_message.split()[2] == "verify" else 1
                server_demand.append(received_message) # Add server demand
                server_demand += self.get_n_server_message(n_server_message)
            encoding_text = server.handle_server_task(last_sent_message, server_demand) #Get encoding text from specific task
            self.send_message("s", encoding_text) # send to server
            server_demand.clear() # Clear array so we can encode again
        get_message = True

    def get_n_server_message(self, n, show=True):
        demand = []
        for i in range(n):
            raw_message, msg_type = self.get_server_message() # Get server message and type of message
            received_message = server.decode_server_message(raw_message) # decode message to make it readable
            demand.append(received_message)# Add server demand
            if show: self.ui.receivedMessage.append(server.construct_message_to_show("Server", received_message))
        return demand

    def test_shift_encoder(self):
        """ Send server message to test shift encoder automatically """
        global auto_test
        auto_test = True
        message = "task shift encode 10"
        self.send_message("s", message)

    def test_vigenere_encoder(self):
        """ Send server message to test vigenere encoder automatically """
        global auto_test
        auto_test = True
        message = "task vigenere encode 10"
        self.ui.receivedMessage.clear()
        self.send_message("s", message)

    def test_rsa_encoder(self):
        """ Send server message to test RSA encoder automatically """
        global auto_test
        auto_test = True
        message = "task RSA encode 10"
        self.ui.receivedMessage.clear()
        self.send_message("s", message)

    def test_hash_hash(self):
        """ Send server message to test message hashing automatically """
        global auto_test
        auto_test = True
        message = "task hash hash"
        self.ui.receivedMessage.clear()
        self.send_message("s", message)

    def test_hash_verify(self):
        """ Send server message to verify if hash is correct automatically """
        global auto_test
        auto_test = True
        message = "task hash verify"
        self.ui.receivedMessage.clear()
        self.send_message("s", message)

    def test_diffie_hellman(self):
        global auto_test
        auto_test = True
        message = "task DifHel"
        self.ui.receivedMessage.clear()
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
