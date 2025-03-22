from cryptography import functions

def handle_server_task(received_message, last_sent_message, shift_server_demand):
    """Traite les messages du serveur nécessitant une action spécifique."""
    
    if len(shift_server_demand) == 2:
        text_to_encode = shift_server_demand[1]
        task_type = last_sent_message.split()[1]

        if task_type == "shift":
            shift = int(get_server_shift(shift_server_demand[0]))
            encoding_text = functions.shift_encoder(text_to_encode, shift)
        elif task_type == "vigenere":
            key = get_server_shift(shift_server_demand[0])
            encoding_text = functions.encrypt_vigenere(text_to_encode, key)
        elif task_type == "RSA":
            n, e = get_server_rsa_infos(shift_server_demand[0])
            message_numbers = functions.numConversion(text_to_encode)
            encoding_text = [functions.encrypt(num, e, n) for num in message_numbers]
        shift_server_demand.clear()
        return encoding_text

def isc_encode(type, message):
    if message:

        message_bytes = bytearray()
        if(isinstance(message, str)):
            #Add each message character encoded in 4 bytes
            for char in message:
                encoded = char.encode('utf-8')
                message_bytes += (4 - len(encoded)) * b'\x00' + encoded
        else:
            message_bytes += message

        msg_length = len(message_bytes) // 4 

        return b"ISC" + type.encode("utf-8") + int(msg_length).to_bytes(2, 'big') + message_bytes

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