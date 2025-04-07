import hashlib
import random

#region Shift encoding
def encrypt_shift(text, shift):
    """
    Encode message in shift algortithm
    text => text to encode
    shift => gap to encode each letters
    """
    encoded_text = bytearray()

    for char in text:
        encoded_text.extend(int.to_bytes(int.from_bytes(char.encode()) + shift, 4))
        
    return encoded_text
#endregion

def generate_key(msg, key):
    """
    Génère une clé de la même longueur que le message en répétant la clé initiale.
    """
    key = (key * (len(msg) // len(key) + 1))[:len(msg)]
    return key

def encrypt_vigenere(msg, key):
    """
    Chiffre un message avec l'algorithme de Vigenère.
    - msg : Texte à chiffrer
    - key : Clé de chiffrement

    Retourne : Message chiffré
    """
    key = generate_key(msg, key)  # Génère une clé de la même longueur que le message
    result = bytearray()

    for i, char in enumerate(msg):
        iChar = int.from_bytes(char.encode())
        iKey = int.from_bytes(key[i % len(key)].encode())
        
        result.extend(int.to_bytes((iChar+iKey), 4))

    return result

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

def encrypt_rsa(n, e, msg):
    result = bytearray()

    for char in msg:
        result.extend(
            int.to_bytes(
                # Compute : c^e mod n
                pow(int.from_bytes(char.encode()), int(e), int(n)), 4))

    return result

def hash_message(msg):
    hashed = hashlib.sha256(msg.encode()).hexdigest()
    return hashed

def generate_prime_number():
    """
    Generate a random prime number between 100 and 1000.
    """
    prime = random.randint(100, 1000)
    while not is_prime(prime):
        prime = random.randint(100, 1000)
    return prime

def is_prime(n):
    """
    Check if a number is prime.
    """
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True