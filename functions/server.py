from datetime import datetime
import functions.cryptography as cryptography

last_sender = ""

def handle_server_task(last_sent_message, server_demand):
    """
    Processes server messages that require a specific action.
    
    Parameters:
    last_sent_message -- the last message sent to the server
    server_demand -- the server's response that may require encryption/hashing

    Returns:
    The result of the processed task (encrypted or hashed message).
    """
    if(len(server_demand) != 0):
        text_to_encode = server_demand[1]
    task_type = last_sent_message.split()[1]

    if task_type == "shift":
        shift = int(get_server_shift(server_demand[0]))
        encoding_text = cryptography.encrypt_shift(text_to_encode, shift)
    elif task_type == "vigenere":
        key = get_server_shift(server_demand[0])
        encoding_text = cryptography.encrypt_vigenere(text_to_encode, key)
    elif task_type == "RSA":
        n, e = get_server_rsa_infos(server_demand[0])
        encoding_text = cryptography.encrypt_rsa(e, n, text_to_encode)
    elif task_type == "hash":
        encoding_text = cryptography.hash_message(text_to_encode)
        hash_type = last_sent_message.split()[2]
        if hash_type == "verify":
            if server_demand[2] == cryptography.hash_message(text_to_encode):
                encoding_text = "true"
            else:
                encoding_text = "false"
    server_demand.clear()
    return encoding_text

def isc_encode(type, message):
    """
    Encodes a message using the ISC protocol format.

    Parameters:
    type -- the type of the message (e.g., 'TEX', 'IMG', etc.)
    message -- the message content (str or bytes)

    Returns:
    A bytes object following the ISC protocol structure.
    """
    if message:
        message_bytes = bytearray()
        if isinstance(message, str):
            # Add each character encoded in 4 bytes
            for char in message:
                encoded = char.encode('utf-8')
                message_bytes += (4 - len(encoded)) * b'\x00' + encoded
        else:
            message_bytes += message

        msg_length = len(message_bytes) // 4 

        return b"ISC" + type.encode("utf-8") + int(msg_length).to_bytes(2, 'big') + message_bytes

def construct_message_to_show(who, message):
    """
    Builds the HTML representation of a chat message.

    Parameters:
    who -- the sender of the message ('Server' or 'You')
    message -- the message content

    Returns:
    A formatted HTML string ready to display in the chat.
    """
    global last_sender
    if ((last_sender == "Server" and who == "Server") or (last_sender == "You" and who == "You")):
        return f'''
        <div><span style="color: gray;">[{message_sending_time()}]</span> {message}</div>
        '''
    last_sender = who
    
    return f'''
    <div style="display: flex; align-items: center;">
        <img src="src/img/ISC.png" width="16" height="12" 
             style="border-radius: 50%; border: 2px solid black; margin-right: 8px;">
        <b>{who}</b>
    </div>
    <div><span style="color: gray;">[{message_sending_time()}]</span> {message}</div>
    '''

def message_sending_time():
    """
    Returns the current time in 'HH:MM' format.
    """
    return datetime.now().strftime("%H:%M")

def get_server_shift(server_shift):
    """
    Extracts the shift key from a server shift message.

    Parameters:
    server_shift -- the server's shift-key formatted string

    Returns:
    The extracted shift key as a string.
    """
    shift = server_shift.split("shift-key ")[1]
    return shift

def get_server_rsa_infos(server_rsa):
    """
    Extracts RSA information (n and e) from the server's RSA message.

    Parameters:
    server_rsa -- the server's RSA info string

    Returns:
    A tuple (e, n) containing the RSA public exponent and modulus.
    """
    infos = server_rsa.split(", e=")
    e = int(infos[1])
    n = int(infos[0].split("n=")[1])
    return (e, n)

def decode_server_message(raw_message):
    """
    Decodes a server message received as raw bytes.

    Parameters:
    raw_message -- the raw bytes message from the server

    Returns:
    A decoded string after removing padding.
    """
    received_message = ""
    for i in range(0, len(raw_message), 4):
        char_data = raw_message[i:i+4]  # Read 4 bytes at a time
        received_message += char_data.decode("utf-8", errors="ignore").strip('\x00')  # Remove padding
    return received_message
