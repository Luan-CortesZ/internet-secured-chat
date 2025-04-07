import sys                                  # For system-level operations and command line arguments
import threading                            # For concurrent execution
from PySide6.QtWidgets import QApplication  # Core PySide6 widgets
from chat_client import ChatClient

def main():
    """
    Main function to initialize and run the chat client application.
    """
    app = QApplication(sys.argv)  # Create a new PySide6 application
    client = ChatClient()         # Create an instance of the chat client
    client.show()                 # Display the client window
    threading.Thread(target=client.display_messages_loop, daemon=True).start()  # Start a new thread to receive response (prevents UI from freezing)
    sys.exit(app.exec())          # Start the application event loop

if __name__ == "__main__":
    main()  # Run the main function when script is executed directly