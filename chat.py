import os
import sys                                  # For system-level operations and command line arguments
import socket                               # For network communication
import threading                            # For concurrent execution
from PySide6.QtWidgets import QApplication, QWidget  # Core PySide6 widgets
from PySide6.QtUiTools import QUiLoader  
from dotenv import load_dotenv
import cryptography_functions

load_dotenv() #Load environment variables

#Get server configuration from env file
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
HEADER = b"ISC" #Message header is always starting by "ISC"
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
        #self.ui = loader.load('./src/views/form.ui', self)  # Load the UI design from file
        self.ui = loader.load('./src/views/ISC_GUI.ui', self)  # Load the UI design from file
        self.setWindowTitle('103.2 - Internet Secured Chat')     # Set window title
        self.ui.btnSend.clicked.connect(self.send_message)  # Connect button click to send_message method
        self.ui.btnShift.clicked.connect(self.test_shift_encoder)
        self.ui.btnVigenere.clicked.connect(self.test_vigenere_encoder)
        self.ui.btnRSA.clicked.connect(self.test_rsa_encoder)
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
            self.close()     
                            # Close the application window

    def send_message(self, type = "", message = ""):
        """
        Send the message entered by the user to the server and prepare to receive a response.
        """
        global last_sent_message
        if message == "" and type == "":
            message = self.ui.userMessage.text().split(" ")[1]      # Get text from the input field
            type = self.ui.userMessage.text().split(" ")[0][1] 
        self.ui.userMessage.setText(f"/{type}")
        if message:                         # Only proceed if message is not empty
            self.ui.receivedMessage.append(f'<You> {message}')  # Display user's message in the chat area
            #Verify if msg is set
            #Message to send with type and length
            user_message_encoded = HEADER + ord(type).to_bytes(1) + len(message).to_bytes(2, 'big')

            #Add each message character encoded in 4 bytes
            for char in message:
                user_message_encoded += ord(char).to_bytes(4, 'big')

            #Send message to server
            self.socket.send(user_message_encoded)

            #Save last sent message
            last_sent_message = message

    def receive_message(self):
        """
        Receive and display the server's response message.
        """
        try:
            (raw_message,msg_type) = self.get_server_message() #Get server message

            received_message = decode_server_message(raw_message) #Decode server message to make it readable
            match msg_type:
                case 't': #User message
                    if(received_message != last_sent_message):
                        self.ui.receivedMessage.append(f'<User> {received_message}')
                case 'i': #Image message
                    self.ui.receivedMessage.append(f'<Image> {received_message}')
                case 's': #Server message
                    self.ui.receivedMessage.append(f'<Server> {received_message}')
                    if("task" in last_sent_message):
                        shift_server_demand.append(received_message)
                        if(len(shift_server_demand) == 2):
                            text_to_encode = shift_server_demand[1]
                            if("shift" in last_sent_message):
                                shift = int(get_server_shift(shift_server_demand[0]))
                                encoding_text = cryptography_functions.shift_encoder(text_to_encode, shift)
                                self.send_message("s", encoding_text)
                            if("vigenere" in last_sent_message):
                                shift = get_server_shift(shift_server_demand[0])
                            if("RSA" in last_sent_message):
                                (n,e) = get_server_rsa_infos(shift_server_demand[0])
                                message_numbers = cryptography_functions.numConversion(text_to_encode) # numerical conversion of message
                                encrypted_numbers = [cryptography_functions.encrypt(num, e, n) for num in message_numbers] # to encrypt each number
                case _:
                    ""
        except socket.error as e:
            print(f"Error receiving message: {e}")  # Print error message if receiving fails

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


def get_server_shift(server_shift):
    """
    Get server shift sent 
    """
    shift = server_shift.split("shift-key ")[1]
    return shift

def get_server_rsa_infos(server_rsa):
    """
    Get server rsa informations

    return n and e
    """
    infos = server_rsa.split(", e=")
    e = int(infos[1])
    n = int(infos[0].split("n=")[1])
    return (e,n)



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
    threading.Thread(target=client.receive_message, daemon=True).start()  # Start a new thread to receive response (prevents UI from freezing)
    sys.exit(app.exec())          # Start the application event loop

if __name__ == "__main__":
    main()  # Run the main function when script is executed directly

