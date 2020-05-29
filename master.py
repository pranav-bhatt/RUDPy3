#master implementation for UDP Hole Punching
#run this on a reachable machine (like an AWS Instance or something)

import socket
import sys

server_listening_port = 3540

sockfd = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sockfd.bind(("", server_listening_port))
print(f"listening on port {server_listening_port}")

client_requests = []

while True:
    data, addr = sockfd.recvfrom(32)
    client_requests.append(addr)
    print(f"Connection from {addr}!")

    if len(client_requests) == 2:
        client_a_ip = client_requests[0][0]
        client_a_port = client_requests[0][1]
        client_b_ip = client_requests[1][0]
        client_b_port = client_requests[1][1]

        sockfd.sendto(f"{client_a_ip}:{client_a_port}".encode(),client_requests[1])
        sockfd.sendto(f"{client_b_ip}:{client_b_port}".encode(),client_requests[0])
        client_requests = []

sockfd.close()