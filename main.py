import os
import sys                                  # For system-level operations and command line arguments
import socket                               # For network communication
import threading                            # For concurrent execution
from PySide6.QtWidgets import QApplication, QWidget  # Core PySide6 widgets
from PySide6.QtUiTools import QUiLoader  
from dotenv import load_dotenv
import functions.server as server

load_dotenv() #Load environment variables

#Get server configuration from env file
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
last_sent_message = ""
shift_server_demand = []

class ChatClient(QWidget):
    """
    A PySide6-based chat client that connects to a server and allows
    sending/receiving messages through a graphical interface.
    """
    def __init__(self, host=HOST, port=PORT):
        """
        Initialize the chat client with server connection details.
        
        Args:
            host (str): Server hostname or IP address (default: localhost)
            port (int): Server port number (default: 12345)
        """
        super(ChatClient, self).__init__()  # Initialize parent QWidget class
        loader = QUiLoader()                # Create a QUiLoader instance
        self.ui = loader.load('./src/views/ISC_GUI.ui', self)  # Load the UI design from file
        self.setWindowTitle('103.2 - Internet Secured Chat')     # Set window title
        self.ui.btnSend.clicked.connect(lambda: self.send_message())  # Connect button click to send_message method
        self.ui.btnShift.clicked.connect(self.test_shift_encoder)
        self.ui.btnVigenere.clicked.connect(self.test_vigenere_encoder)
        self.ui.btnRSA.clicked.connect(self.test_rsa_encoder)
        self.ui.userMessage.setText("/")
        self.ui.userMessage.returnPressed.connect(self.send_message)
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
        """
        global last_sent_message

        type = type or self.ui.userMessage.text()[1]
        message = message or self.ui.userMessage.text()[3:]
            
        self.ui.userMessage.setText(f"/{type}")

        text_to_show = message if isinstance(message, str) else bytes(byte for byte in message if byte != 0).decode('utf-8', 'replace')
        self.ui.receivedMessage.append(server.construct_message_to_show("You", text_to_show))  # Display user's message in the chat area

        #Send message to server
        self.socket.send(server.isc_encode(type, message))
        last_sent_message = text_to_show

    def receive_message(self):
        """Réception et affichage des messages du serveur."""
        global last_sent_message
        global shift_server_demand

        try:
            raw_message, msg_type = self.get_server_message()
            received_message = server.decode_server_message(raw_message)

            if msg_type == 't' and received_message != last_sent_message:
                self.ui.receivedMessage.append(server.construct_message_to_show("User", received_message))
            elif msg_type == 'i':
                self.ui.receivedMessage.append(server.construct_message_to_show("Image", received_message))
            elif msg_type == 's':
                self.ui.receivedMessage.append(server.construct_message_to_show("Server", received_message))
                if("task" in last_sent_message):
                    shift_server_demand.append(received_message)
                    if len(shift_server_demand) == 2:
                        encoding_text = server.handle_server_task(last_sent_message, shift_server_demand) 
                        self.send_message("s", encoding_text)
                        shift_server_demand.clear()
        
        except (socket.error, ValueError) as e:
            print(f"Erreur réception : {e}")
    
    def receive_messages_loop(self):
        """
        Loop to continuously receive messages from the server.
        """
        while True:
            try:
                self.receive_message()
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
        message = "task shift encode 10"
        self.send_message("s", message)

    def test_vigenere_encoder(self):
        message = "task vigenere encode 10"
        self.send_message("s", message)

    def test_rsa_encoder(self):
        message = "task RSA encode 10"
        self.send_message("s", message)

def closeEvent(self, event):
    """
    Handle the window close event by properly closing the socket connection.
    
    Args:
        event: The close event object
    """
    self.socket.close()  # Close the socket connection
    event.accept()       # Accept the close event

def main():
    """
    Main function to initialize and run the chat client application.
    """
    app = QApplication(sys.argv)  # Create a new PySide6 application
    client = ChatClient()         # Create an instance of the chat client
    client.show()                 # Display the client window
    threading.Thread(target=client.receive_messages_loop, daemon=True).start()  # Start a new thread to receive response (prevents UI from freezing)
    sys.exit(app.exec())          # Start the application event loop

if __name__ == "__main__":
    main()  # Run the main function when script is executed directly

