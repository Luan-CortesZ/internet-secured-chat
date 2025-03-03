def shift_encoder(text, shift):
    encoded_text = ""

    for char in text:
        encoded_text += chr(ord(char) + shift)

    return encoded_text