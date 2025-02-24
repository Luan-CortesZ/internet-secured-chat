import socket
server_ip = "vlbelintrocrypto.hevs.ch"  # replace with the server's IP address
server_port = 6000

#Create header "ISC" in byte
header = b"ISC"
#Create client 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Connect client to server
client.connect((server_ip, server_port))


message_type = input("Type of message \nt: Text message\ns: Server-only message\ni: Image message\n")

while True:
    #Type of message
    msg = input("Enter message: ") #Message to send
    
    #Message to send with length
    completeMsg = header + ord(message_type).to_bytes(1) + len(msg).to_bytes(2, 'big')

    for char in msg:
        completeMsg += ord(char).to_bytes(4, 'big')
    print(completeMsg)

    client.send(completeMsg)

    