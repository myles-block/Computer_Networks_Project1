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
BACKUP = "last_seen_terminal2.txt"#TODO: Make a file of this for thie function to run
OUTPUTFILE = "traceroute_data.json" #TODO: Make a file of this for it to run



def traceroute(ipaddress): #start, end, maximum_hops,
    try:
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
        host = str(ipaddress)
        
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
        with open(OUTPUTFILE, 'a') as file:# writes to files
            while True:
                if ttl == 7: #TODO: Change this to your max hops
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
                    place_put = f"{addr[0]}"
                    # print(f"{ttl}: {addr[0]}")
                else:
                    place_put = "No Reply"
                    # print(f"{ttl} *  *  *")
                hopJSON = addHopData(ttl, place_put)
                connected_list.append(hopJSON)
                if done:
                    break
                ttl += 1
            object = createJSON(host, connected_list)
            TEMPLATIZEDJSON.append(object)
            json.dump(object, file, indent = 4)
            pushToMongoDB(object) # TODO: Comment this out if you are not using mongoDB
            with open(BACKUP, "w") as file:
                file.write(str(host))
            file.close()
            print(f"{host} ({dest_addr} Traceroute completed & Recorded.")
    except KeyboardInterrupt:
        print("Traceroute stopped by user.")
    

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

def createJSON(ipaddress, attachment_list):
    ip_address = {
    "location" : "LKD",  # TODO: changed this based on location
    "ip_address_host" : ipaddress,
    "ip_address_attach" : attachment_list,
    }
    return ip_address


def pushToMongoDB(object):
    dbname = get_database()
    collection_name = dbname["myles_ipLists"]
    collection_name.insert_one(object)

def addHopData(ttl, ip):
    hop_data = {
        "hop": ttl,
        "ip": ip
    }
    return hop_data


#router_iterator("10.2.154.185", "10.2.200.0") # TODO: change this to your IP range split
router_iterator("10.8.247.48", "10.9.0.0") # terminal 2
#router_iterator("10.12.204.206", "10.19.51.51") # terminal 3
#router_iterator("10.19.51.52", "10.25.153.153") # terminal 4
# router_iterator("10.25.153.154", "10.31.255.255") # terminal 5
#router_iterator("10.31.255.255", "10.38.102.101") # terminal 6
#router_iterator("10.38.102.102", "10.44.204.203") # terminal 7
#router_iterator("10.44.204.204", "10.51.51.49") # terminal 8
#router_iterator("10.51.51.50", "10.57.153.151") # terminal 9
#router_iterator("10.57.153.152", "10.64.0.1") # terminal 10
print(TEMPLATIZEDJSON)


