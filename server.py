import socket
import threading
import hashlib
import time
import datetime
import random

# PLP Simulation settings
lossSimualation = False

# Delimiter
delimiter = "|:|:|"
delimiter_msg = "?:?:?"

# Seq number flag
seqFlag = 0

# Packet class definition
class packet():
    checksum = 0
    length = 0
    seqNo = 0
    msg = 0

    def make(self, data):
        self.msg = data
        self.length = str(len(data))
        self.checksum=hashlib.sha1(data).hexdigest()
        print("Length: %s\nSequence number: %s" % (self.length, self.seqNo))


# Connection handler
def handleConnection(address, data):
    drop_count=0
    packet_count=0
    time.sleep(0.5)
    if lossSimualation:
        packet_loss_percentage=float(input("Set PLP (0-99)%: "))/100.0
        while packet_loss_percentage<0 or packet_loss_percentage >= 1:
          packet_loss_percentage = float(input("Enter a valid PLP value. Set PLP (0-99)%: "))/100.0
    else:
        packet_loss_percentage = 0
    start_time=time.time()
    print("Request started at: " + str(datetime.datetime.utcnow()))
    pkt = packet()
    threadSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Read requested file

        try:
            print("Opening file %s" % data)
            fileRead = open(data, 'rb')
            data = fileRead.read()
            fileRead.close()
        except:
            msg="FNF"
            pkt.make(msg)
            finalPacket = f"{pkt.checksum}{delimiter}{pkt.seqNo}{delimiter}{pkt.length}{delimiter_msg}{pkt.msg}".encode() 
            threadSock.sendto(finalPacket, address)
            print("Requested file could not be found, replied with FNF")
            return

        # Fragment and send file 500 byte by 500 byte
        x = 0
        while x < (len(data) / 2048) + 1:
            packet_count += 1
            randomised_plp = random.random()
            if packet_loss_percentage < randomised_plp:
                msg = data[x * 2048:x * 2048 + 2048]
                pkt.make(msg)
                if not pkt.msg:
                    break
                finalPacket = f"{pkt.checksum}{delimiter}{pkt.seqNo}{delimiter}{pkt.length}{delimiter_msg}".encode() + pkt.msg
                # Send packet
                sent = threadSock.sendto(finalPacket, address)
                print('Sent %s bytes back to %s, awaiting acknowledgment..' % (sent, address))
                threadSock.settimeout(2)
                try:
                    ack, address = threadSock.recvfrom(100)
                except:
                    print("Time out reached, resending ...%s" % x)
                    continue
                if ack.decode().split(",")[0] == str(pkt.seqNo):
                    pkt.seqNo = int(not pkt.seqNo)
                    print("Acknowledged!")
                    x += 1
            else:
                print("\n------------------------------\n\t\tDropped packet\n------------------------------\n")
                drop_count += 1
        print("Packets served: " + str(packet_count))
        if lossSimualation:
            print("Dropped packets: " + str(drop_count)+"\nComputed drop rate: %.2f" % float(float(drop_count)/float(packet_count)*100.0))
    except:
        print("Internal server error")

#If you want to implement UDP Hole Punching

"""
master = ("<insert_server_ip>",3540)

try:
    sockfd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sockfd.settimeout(60)
    sockfd.bind(('',0))
    sockfd.sendto("".encode(),master)

except socket.error:
    print("Failed :( ")
    sys.exit()

peer_data, addr = sockfd.recvfrom(1024)
print(peer_data.decode())

print("Trying to initiate comms...")
peer_ip = peer_data.decode().split(":")[0]
peer_port = int(peer_data.decode().split(":")[1])
sockfd.sendto("hello".encode(),(peer_ip,peer_port))
"""
#local testing

# Set address and port
serverAddress = "localhost"
serverPort = 10000

# Start - Connection initiation
sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the port
server_address = (serverAddress, serverPort)
print('Starting up on %s port %s' % server_address)
sockfd.bind(server_address)

# Listening for requests indefinitely
while True:
    print('Waiting to receive message')
    data, address = sockfd.recvfrom(600)
    connectionThread = threading.Thread(target=handleConnection, args=(address, data.decode()))
    connectionThread.start()
    print('Received %s bytes from %s' % (len(data), address))