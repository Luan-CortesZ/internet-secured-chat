import hashlib
import random
from sympy import primitive_root

#region Shift encoding
def encrypt_shift(text, shift):
    """
    Encrypts a message using a basic shift algorithm (similar to Caesar cipher).
    
    Parameters:
    text -- the text to encrypt
    shift -- the number of positions to shift each character

    Returns:
    A bytearray containing the shifted and encoded text.
    """
    encoded_text = bytearray()

    for char in text:
        encoded_text.extend(int.to_bytes(int.from_bytes(char.encode()) + shift, 4))
        
    return encoded_text
#endregion

def generate_key(msg, key):
    """
    Generates a key of the same length as the message by repeating the initial key.

    Parameters:
    msg -- the message to encrypt or decrypt
    key -- the base key

    Returns:
    A key string matching the length of the message.
    """
    key = (key * (len(msg) // len(key) + 1))[:len(msg)]
    return key

def encrypt_vigenere(msg, key):
    """
    Encrypts a message using the Vigenère cipher algorithm.

    Parameters:
    msg -- the text to encrypt
    key -- the encryption key

    Returns:
    A bytearray containing the encrypted message.
    """
    key = generate_key(msg, key)  # Generate a key matching the length of the message
    result = bytearray()

    for i, char in enumerate(msg):
        iChar = int.from_bytes(char.encode())
        iKey = int.from_bytes(key[i].encode())
        
        result.extend(int.to_bytes((iChar + iKey), 4))

    return result

def decrypt_vigenere(msg, key):
    """
    Decrypts a message encrypted with the Vigenère cipher algorithm.

    Parameters:
    msg -- the message to decrypt
    key -- the decryption key

    Returns:
    The decrypted message as a string.
    """
    decrypted_text = []
    key = generate_key(msg, key)

    for i in range(len(msg)):
        char = msg[i]
        if char.isupper():  # Decrypt uppercase letters
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('A'))
        elif char.islower():  # Decrypt lowercase letters
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('a'))
        else:  # Leave non-alphabetic characters unchanged
            decrypted_char = char
        decrypted_text.append(decrypted_char)

    return "".join(decrypted_text)
#endregion

def encrypt_rsa(n, e, msg):
    """
    Encrypts a message using the RSA algorithm.

    Parameters:
    n -- RSA modulus
    e -- RSA public exponent
    msg -- the message to encrypt

    Returns:
    A bytearray containing the RSA encrypted message.
    """
    result = bytearray()

    for char in msg:
        result.extend(
            int.to_bytes(
                # Compute: (char ^ e) mod n
                pow(int.from_bytes(char.encode()), int(e), int(n)), 4))

    return result

def hash_message(msg):
    """
    Hashes a message using SHA-256.

    Parameters:
    msg -- the message to hash

    Returns:
    A hexadecimal string representing the SHA-256 hash.
    """
    hashed = hashlib.sha256(msg.encode()).hexdigest()
    return hashed

def get_diffie_hellman_prime():
    """
    Generates a random prime and its primitive root for Diffie-Hellman key exchange.

    Returns:
    A tuple (prime modulus, generator).
    """
    modulo = generate_prime_number()
    generator = primitive_root(modulo)
    return modulo, generator

def get_exchange_key(G, a, p):
    """
    Computes a Diffie-Hellman partial key.

    Parameters:
    G -- generator
    a -- private key
    p -- prime modulus

    Returns:
    The computed partial key (G^a mod p).
    """
    return pow(G, a, p)

def generate_prime_number():
    """
    Generates a random prime number between 2 and 4999.

    Returns:
    A prime number.
    """
    prime = random.randint(2, 4999)
    while not is_prime(prime):
        prime = random.randint(2, 4999)
    return prime

def is_prime(n):
    """
    Checks if a number is a prime.

    Parameters:
    n -- the number to check

    Returns:
    True if n is prime, False otherwise.
    """
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
