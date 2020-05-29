import socket
import hashlib
import os
from sys import exit

#If you want to implement UDP Hole Punching

"""
master = ("<insert_server_ip>",3540)

try:
    sockfd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sockfd.settimeout(10)
    sockfd.bind(('',0))
    sockfd.sendto("".encode(),master)

except socket.error:
    print("Failed :( ")
    exit()

peer_data, addr = sockfd.recvfrom(1024)
print(peer_data.decode())

print("Trying to initiate comms...")
peer_ip = peer_data.decode().split(":")[0]
peer_port = int(peer_data.decode().split(":")[1])

# Set address and port
serverAddress = peer_ip
serverPort = peer_port
"""

serverAddress = 'localhost'
serverPort = 10000
sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockfd.settimeout(10)


# Delimiter
delimiter = "|:|:|"
delimiter_msg = b"?:?:?"

# Start - Connection initiation
while 1:
    #By default 'r_' is appended to filename !!!!!!!!!!!!!!!!!!!!!!!!
    server_address = (serverAddress, serverPort)
    userInput = input("\nRequested file: ")
    message = userInput
    seqNoFlag = 0
    f = open("r_" + userInput, 'wb')
    
    #Uncomment if you want to implement UDP Hole Punching !!!!!!!!!!!
    #x,y = sockfd.recvfrom(50)

    try:
        # Connection trials
        connection_trials_count=0
        # Send data
        print('Requesting %s' % message)
        sent = sockfd.sendto(message.encode(), server_address)
        # Receive indefinitely
        while 1:
            # Receive response
            print('\nWaiting to receive..')
            try:
                data, server = sockfd.recvfrom(4096)
                # Reset failed trials on successful transmission
                connection_trials_count=0
            except:
                connection_trials_count += 1
                if connection_trials_count < 5:
                    print("\nConnection time out, retrying")
                    continue
                else:
                    print("\nMaximum connection trials reached, skipping request\n")
                    os.remove("r_" + userInput)
                    break
            seqNo = data.split(delimiter_msg)[0].decode().split(delimiter)[1]
            clientHash = hashlib.sha1(data.split(delimiter_msg)[1]).hexdigest()
            print("Server hash: " + data.split(delimiter_msg)[0].decode().split(delimiter)[0])
            print("Client hash: " + clientHash)
            if data.split(delimiter_msg)[0].decode().split(delimiter)[0] == clientHash and seqNoFlag == int(seqNo == True):
                packetLength = data.split(delimiter_msg)[0].decode().split(delimiter)[2]
            
                if data.split(delimiter_msg)[1] == "FNF".encode():
                    print ("Requested file could not be found on the server")
                    os.remove("r_" + userInput)
                else:
                    f.write(data.split(delimiter_msg)[1])
                print("Sequence number: %s\nLength: %s" % (seqNo, packetLength))
                print("Server: %s on port %s" % server)
                sent = sockfd.sendto((str(seqNo) + "," + packetLength).encode(), server)
            else:
                print("Checksum mismatch detected, dropping packet")
                print("Server: %s on port %s" % server)
                continue
            if int(packetLength) < 2048:
                seqNo = int(not seqNo)
                break

    finally:
        print("Closing socket")
        sockfd.close()
        f.close()