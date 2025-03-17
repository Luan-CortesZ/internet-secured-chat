import math

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

#region RSA Encoding
def power(base, expo, m): # to compute modular exponentiation
    res = 1
    base = base % m
    while expo > 0:
        if expo & 1: #odd expo > multiply base with res
            res = (res * base) % m
        base = (base * base) % m #square the base
        expo = expo // 2 #reduce expponent by half
    return res 

def modInverse(e,phi): #find modular inverse of e % phi(n)
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

    
n = 1425646933
phi =   euler_totient(n)
e = 7014323
d = modInverse(e,phi)


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