import socket  # Allows you to work with network sockets & sending/receiving data
import struct  # Used to encode and decode structured data
import ipaddress
import time  # Used to keep track of data and when operations occur
from datetime import datetime  # Gets current time and date

# Constants
TIMEOUT = 4  # How long program waits to receive a response from a node or hop
PORT = 33434  # Transmits packets to a remote host and uses the responses to map the path

# Protocols
ICMP = socket.getprotobyname('icmp')  # Retrieves the protocol number associated with Internet Control Message Protocol (ICMP) protocol
UDP = socket.getprotobyname('udp')  # Retrieves the protocol number associated with User Datagram Protocol(UDP)



def traceroute(ipaddress): #start, end, maximum_hops,
    '''
    param1: start
    param2: end
    param3: maximum_hops
    '''
    # Sets up a socket for sending & receiving ICMP and UDP packets at the raw socket level
    # AF_INET = Specifies address family (IPv4)
    # SOCK_RAW = Specifies socket type: raw (lower-level communication protocols)
    # SOCK_DGRAM = Specifies type of socket as datagram socket / discrete packets
    icmp_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP)
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, UDP)

    # Setting a socket option for 'icmp_sock'
    # socket.SOL_SOCKET: Specifies option level
    # SOL_SOCKET: Changes the options within the socket
    # socket.SO_RCVTIMEO: Socket option that defines how long the socket waits to receive data before timed out
    icmp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack('ll', TIMEOUT, 0))

    # Hostname input
    host = str(ipaddress)#input("Please enter the hostname to traceroute: ")

    try:
        dest_addr = socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Cannot resolve '{host}': Unknown host")
        exit(1)

    # Initialization of Time to Live (TTL)
    ttl = 1

    # Tracerouting Process
    print(f"Tracerouting... {host} ({dest_addr})")
    while True:
        if ttl == 2: #TODO: This is our max ttl we are letting it go
            break
        udp_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        udp_sock.sendto(b'', (dest_addr, PORT))
        start_time = time.time()
        no_tries = 3
        success = False
        done = False

        # Receiving packet
        while no_tries > 0:
            try:
                packet, addr = icmp_sock.recvfrom(512)
                success = True
            except socket.error:
                no_tries -= 1
                continue
            if addr[0] == dest_addr:
                done = True
                break

        # Output information or timeout
        if success:
            end_time = time.time()
            name = ""
            try:
                name = socket.gethostbyaddr(addr[0])[0]
            except socket.herror:
                pass
            t = round((end_time - start_time) * 1000, 4)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{ttl}: {addr[0]}")
        else:
            print(f"{ttl} *  *  *")

        if done:
            break
        ttl += 1

    # Completion message
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} Traceroute completed.")


def router_iterator(start, end):
    start_ip = ipaddress.IPv4Address(start)
    end_ip = ipaddress.IPv4Address(end)
    
    while start_ip <= end_ip:
        traceroute(start_ip)
        start_ip += 8

router_iterator("10.0.0.1", "10.0.0.255")
