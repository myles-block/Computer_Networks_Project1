from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process
import socket  # Allows you to work with network sockets & sending/receiving data
import struct  # Used to encode and decode structured data
import ipaddress # Used to ipaddress math (skipping 8 ips in between)
import time  # Used to keep track of data and when operations occur
import json
from datetime import datetime  # Gets current time and date
from pymongo_get_database import get_database #grabs the MongoDB database
from progress.bar import Bar #adds progress bar for loading
from progress.spinner import MoonSpinner

# Constants
TIMEOUT = 4  # How long program waits to receive a response from a node or hop
PORT = 33434  # Transmits packets to a remote host and uses the responses to map the path

# Protocols
ICMP = socket.getprotobyname('icmp')  # Retrieves the protocol number associated with Internet Control Message Protocol (ICMP) protocol
UDP = socket.getprotobyname('udp')  # Retrieves the protocol number associated with User Datagram Protocol(UDP)
IPLIST = []
TEMPLATIZEDJSON = []


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

    # Hostname & connected_list
    host = str(ipaddress)#input("Please enter the hostname to traceroute: ")
    
    connected_list = []

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
        if ttl == 3: #TODO: This is our max hops we are letting it go
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
            place_put = f"{addr[0]}"
            # print(f"{ttl}: {addr[0]}")
        else:
            place_put = "*"
            # print(f"{ttl} *  *  *")
        hopJSON = addHopData(ttl, place_put)
        connected_list.append(hopJSON)
        if done:
            break
        ttl += 1
    object = createJSON(host, connected_list)
    TEMPLATIZEDJSON.append(object)


    # Completion message
    # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{host} ({dest_addr} Traceroute completed.")

def traceroute_with_threads(lists_of_ip):
    with ThreadPoolExecutor() as executor:
        executor.map(traceroute, lists_of_ip)

def router_iterator(start, end):
    start_ip = ipaddress.IPv4Address(start)
    end_ip = ipaddress.IPv4Address(end)
    while start_ip <= end_ip:
        IPLIST.append(start_ip)
        start_ip += 8
    traceroute_with_threads(IPLIST)
    writeToJSON(TEMPLATIZEDJSON)

def createJSON(ipaddress, attachment_list):
    ip_address = {
    # "whodidit" : "Myles", #TODO: change this based on who is using the file 
    "location" : "iLab",  # TODO: changed this based on location
    "ip_address_host" : ipaddress,
    "ip_address_attach" : attachment_list,
    }
    return ip_address


def pushToMongoDB():
    dbname = get_database()
    collection_name = dbname["myles_data"]
    collection_name.insert_many(TEMPLATIZEDJSON)

def writeToJSON(object):
    with open("IPCollect.json", "a") as line:
        json.dump(object, line, indent=4)

def addHopData(ttl, ip):
    hop_data = {
        "hop": ttl,
        "ip": ip
    }
    return hop_data


router_iterator("10.0.0.1", "10.0.0.81") # TODO: change this to your IP range split
# writeToJSON()
print(TEMPLATIZEDJSON)
# pushToMongoDB() # this pushes to mongoDB


