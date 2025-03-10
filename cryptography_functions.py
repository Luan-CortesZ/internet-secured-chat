#region Shift encoding
def shift_encoder(text, shift):
    """
    Encode message in shift algortithm
    text => text to encode
    shift => gap to encode each letters
    """
    encoded_text = ""

    for char in text:
        encoded_text += chr(ord(char) + shift)

    return encoded_text
#endregion

#region Vigenere Encoding
def generate_key (msg, key):
    """
    Generate Vigenere key to have same length than message
    msg => message to encrypt
    key => Key used to encrypt

    return key repeated to have same length than message
    """

    key = list(key)
    if len(msg) == len(key):
        return key
    else: # Extend the key by repeating characters cyclically
        for i in range (len(msg) - len(key)):
            key.append(key[i % len(key)])
        return "".join(key)   

def encrypt_vigenere(msg, key):
    """
    Encrypt message in Vigenere algorithm
    msg => message to encrypt
    key => Key used to encrypt message

    return encrypted message in vigenere
    """
    encrypted_text = []
    key = generate_key(msg, key) # Ensure key length matches message length
    for i in range(len(msg)):
        char = msg[i]
        if char.isupper(): # Encrypt uppercase letters
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('A')) % 26 + ord('A'))
        elif char.islower(): # Encrypt lowercase letters
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('a')) % 26 + ord('a'))
        else: # Keep non-alphabetic characters unchanged
            encrypted_char = char
        encrypted_text.append(encrypted_char)
    return "".join(encrypted_text) # Convert list to string and return

def decrypt_vigenere(msg,key):
    """
    Decrypt message with Vigenere algorithm

    msg => message to decrypt
    key => key used to decrypt message

    return message decrypted
    """
    decrypted_text = []
    key = generate_key(msg,key)
    for i in range(len(msg)):  
        char = msg[i]
        if char.isupper(): # Decrypt uppercase letters
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('A'))
        elif char.islower(): # Decrypt lowercase letters
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('a'))
        else:  # Keep non-alphabetic characters unchanged
            decrypted_char = char
        decrypted_text.append(decrypted_char)
    return "".join(decrypted_text)
#endregion