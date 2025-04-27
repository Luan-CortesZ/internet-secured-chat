import random
import socket  # For network communication
from PySide6.QtWidgets import QWidget  # Core PySide6 widgets
from PySide6.QtUiTools import QUiLoader  # For loading .ui files
from PySide6.QtCore import Signal, QTimer  # Core PySide6 functionalities
import functions.server as server
from functions import cryptography

# Server configuration
HOST = "vlbelintrocrypto.hevs.ch"
PORT = 6000

# Global variables
last_sent_message = ""  # Last message sent by user
server_demand = []      # Stores server-specific encoding tasks
get_message = True      # Controls whether client listens for incoming messages
auto_test = False       # Indicates if auto-test mode is enabled

class ChatClient(QWidget):
    """
    A PySide6-based chat client for communicating with a secure server.
    Handles user interaction and message encoding/decoding.
    """
    message_received = Signal(str)  # Signal to update UI with a received message

    def __init__(self, host=HOST, port=PORT):
        """
        Initialize the chat client, set up the UI, connect to the server.
        """
        super(ChatClient, self).__init__()

        loader = QUiLoader()  # UI loader
        
        # Load UI from file
        self.ui = loader.load('./src/views/ISC_GUI.ui', self)
        self.setWindowTitle('103.2 - Internet Secured Chat')

        # Button event handlers
        self.ui.btnSend.clicked.connect(lambda: self.send_message())
        self.ui.btnShift.clicked.connect(self.test_shift_encoder)
        self.ui.btnVigenere.clicked.connect(self.test_vigenere_encoder)
        self.ui.btnRSA.clicked.connect(self.test_rsa_encoder)
        self.ui.btnHashHash.clicked.connect(self.test_hash_hash)
        self.ui.btnHashVerify.clicked.connect(self.test_hash_verify)
        self.ui.btnDH.clicked.connect(self.test_diffie_hellman)
        
        self.ui.userMessage.setText("/")  # Initialize input with "/"
        self.ui.userMessage.returnPressed.connect(self.send_message)  # Allow sending with Enter key

        self.message_received.connect(self.display_in_ui)  # Link signal to display method

        self.socket = socket.socket()  # TCP socket for communication
        self.connect_to_server(host, port)  # Attempt connection

    def display_in_ui(self, text):
        """ Append received text into the message box (executed on UI thread). """
        self.ui.receivedMessage.append(text)

    def connect_to_server(self, host, port):
        """ Connect to the chat server. """
        try:
            self.socket.connect((host, port))
        except socket.error as e:
            print(f"Error connecting to server: {e}")
            self.close()

    def send_message(self, type="", message=""):
        """
        Send a formatted message to the server.
        Args:
            type (str): Message type ('s', 't', 'i')
            message (str): The message content
        """
        global last_sent_message, get_message
        get_message = False  # Pause message listening

        # Default to message box content if arguments are empty
        type = type or self.ui.userMessage.text()[1]
        message = message or self.ui.userMessage.text()[3:]

        self.ui.userMessage.setText(f"/{type}")  # Prepare next input

        # Convert message to string if needed
        text_to_show = message if isinstance(message, str) else bytes(byte for byte in message if byte != 0).decode('utf-8', 'replace')

        self.message_received.emit(server.construct_message_to_show("You", text_to_show))  # Show own message
        self.socket.sendall(server.isc_encode(type, message))  # Send encoded message

        last_sent_message = text_to_show
        get_message = True  # Resume message listening

    def display_message(self):
        """
        Process and display a message received from the server.
        """
        global last_sent_message, auto_test

        try:
            if not self.socket:
                print("Socket closed, stopping message reception.")
                return

            raw_message, msg_type = self.get_server_message()
            received_message = server.decode_server_message(raw_message)

            if msg_type == 't' and received_message != last_sent_message:
                self.message_received.emit(server.construct_message_to_show("User", received_message))
            elif msg_type == 'i':
                # Image handling would be implemented here
                pass
            elif msg_type == 's':
                self.message_received.emit(server.construct_message_to_show("Server", received_message))
                if auto_test:
                    self.test_server_demand(received_message)
                    auto_test = False

        except (socket.error, ValueError) as e:
            print(f"Reception error: {e}")

    def display_messages_loop(self):
        """
        Continuously check for incoming messages from server.
        """
        global get_message

        while self.socket and get_message:
            try:
                self.display_message()
            except (socket.error, ConnectionResetError):
                print("Connection lost with server.")
                break

    def get_server_message(self):
        """
        Retrieve a raw message and its type from the server.
        Returns:
            tuple(raw_message, message_type)
        """
        receivedHeader = self.socket.recv(6)

        msg_type = receivedHeader[3:4].decode()
        msg_size = int.from_bytes(receivedHeader[4:6], 'big')

        raw_data = self.socket.recv(msg_size * 4)

        return (raw_data, msg_type)

    def test_server_demand(self, received_message):
        """
        Handle server tasks automatically when in auto_test mode.
        """
        global get_message, server_demand

        get_message = False
        myNumber = random.randint(2, 50)

        if "DifHel" in last_sent_message:
            modulo, generator = cryptography.get_diffie_hellman_prime()
            sendNumber = pow(generator, myNumber, modulo)
            self.send_message("s", f"{modulo},{generator}")
            server_demand += self.get_n_server_message(2)
            self.send_message("s", str(sendNumber))
            exchange_key = cryptography.get_exchange_key(int(server_demand[1]), myNumber, modulo)
            server_demand += self.get_n_server_message(1)
            self.send_message("s", str(exchange_key))

        elif "task" in last_sent_message:
            if len(last_sent_message.split()) > 2:
                n_server_message = 2 if last_sent_message.split()[2] == "verify" else 1
                server_demand.append(received_message)
                server_demand += self.get_n_server_message(n_server_message)

            encoding_text = server.handle_server_task(last_sent_message, server_demand)
            self.send_message("s", encoding_text)

        server_demand.clear()
        get_message = True

    def get_n_server_message(self, n, show=True):
        """
        Receive 'n' messages from the server.
        Args:
            n (int): number of messages
            show (bool): if True, display them in the UI
        Returns:
            list of received messages
        """
        demand = []
        for _ in range(n):
            raw_message, msg_type = self.get_server_message()
            received_message = server.decode_server_message(raw_message)
            demand.append(received_message)
            if show:
                self.message_received.emit(server.construct_message_to_show("Server", received_message))
        return demand

    # --- Auto-test methods ---

    def test_shift_encoder(self):
        """ Test shift encoder functionality by sending a predefined task. """
        global auto_test
        auto_test = True
        message = "task shift encode 10"
        QTimer.singleShot(0, self.ui.receivedMessage.clear)
        self.send_message("s", message)

    def test_vigenere_encoder(self):
        """ Test vigenere encoder functionality by sending a predefined task. """
        global auto_test
        auto_test = True
        message = "task vigenere encode 10"
        QTimer.singleShot(0, self.ui.receivedMessage.clear)
        self.send_message("s", message)

    def test_rsa_encoder(self):
        """ Test RSA encoder functionality by sending a predefined task. """
        global auto_test
        auto_test = True
        message = "task RSA encode 10"
        QTimer.singleShot(0, self.ui.receivedMessage.clear)
        self.send_message("s", message)

    def test_hash_hash(self):
        """ Test hash generation functionality. """
        global auto_test
        auto_test = True
        message = "task hash hash"
        QTimer.singleShot(0, self.ui.receivedMessage.clear)
        self.send_message("s", message)

    def test_hash_verify(self):
        """ Test hash verification functionality. """
        global auto_test
        auto_test = True
        message = "task hash verify"
        QTimer.singleShot(0, self.ui.receivedMessage.clear)
        self.send_message("s", message)

    def test_diffie_hellman(self):
        """ Test Diffie-Hellman key exchange process. """
        global auto_test
        auto_test = True
        message = "task DifHel"
        QTimer.singleShot(0, self.ui.receivedMessage.clear)
        self.send_message("s", message)

    def closeEvent(self, event):
        """
        Handle application closure by properly shutting down the socket.
        """
        print("Closing application...")
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except Exception as e:
            print(f"Error closing socket: {e}")

        event.accept()