import math

#region Shift encoding
def shift_encoder(text, shift):
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
    encrypted_text = []
    key = generate_key(msg, key)  # Génère une clé de la même longueur que le message
    
    for i, char in enumerate(msg):
        if char.isupper():  # Lettres majuscules
            encrypted_char = chr((ord(char) - ord('A') + (ord(key[i]) - ord('A'))) % 26 + ord('A'))
        elif char.islower():  # Lettres minuscules
            encrypted_char = chr((ord(char) - ord('a') + (ord(key[i]) - ord('a'))) % 26 + ord('a'))
        else:  # Caractères non alphabétiques (on les garde inchangés)
            encrypted_char = char
        
        encrypted_text.append(encrypted_char)

    return "".join(encrypted_text)


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

#region RSA Encoding
def power(base, expo, m): # to compute modular exponentiation
    res = 1
    base = base % m
    while expo > 0:
        if expo & 1: #odd expo > multiply base with res
            res = (res * base) % m
        base = (base * base) % m #square the base
        expo = expo // 2 #reduce expponent by half
    return str(res) 

def modInverse(e,n): #find modular inverse of e % phi(n)
    phi = euler_totient(n)
    for d in range(2,phi):
        if (e*d)% phi == 1:
            return d
    return -1 #if no valid d is found 


# keys 

def prime_factors(n): # Function to find the prime factors of n
    factors = []
    
    # Check for number of 2s
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    
    # Check for odd factors
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        while n % i == 0:
            factors.append(i)
            n //= i
    
    # If n is a prime number greater than 2
    if n > 2:
        factors.append(n)
    
    return factors


def euler_totient(n):  # Function to compute Euler's Totient Function (φ(n))
    # Factor n into primes p and q
    factors = prime_factors(n)
    
    # Check if n is a product of exactly two primes (p * q)
    if len(factors) == 2 and factors[0] != factors[1]:
        p = factors[0]
        q = factors[1]
        # Compute φ(n) = (p - 1)(q - 1)
        return (p - 1) * (q - 1)
    else:
        raise ValueError("n must be a product of exactly two distinct primes")

    
# Encrypt message using public key (e, n)
def encrypt(msg, e, n):
    return power(msg, e, n)

# Decrypt message using private key (d, n)
def decrypt(c, d, n):
    return power(c, d, n)

# Convert text to a list of numbers (ASCII values)
def numConversion(message):
    return [ord(char) for char in message]

# Convert a list of numbers back to text
def numbers_to_text(numbers):
    return ''.join(chr(num) for num in numbers)


M = "" # Message to encrypt
message_numbers = numConversion(M) # numerical conversion of message
encrypted_numbers = [encrypt(num, e, n) for num in message_numbers] # to encrypt each number
decrypted_numbers = [decrypt(num, d, n) for num in encrypted_numbers] # to decrypt each number
decrypted_message = numbers_to_text(decrypted_numbers) # Convert numbers back to text