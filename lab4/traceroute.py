import socket
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

def checksum(data):
    csum = 0
    countTo = (len(data) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = data[count] * 256 + data[count+1]
        csum += thisVal
        csum &= 0xffffffff
        count += 2
    if countTo < len(data):
        csum += data[-1] << 8
        csum &= 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum += csum >> 16
    answer = ~csum
    answer &= 0xffff
    answer = (answer >> 8) | ((answer << 8) & 0xff00)
    return answer

def build_packet():
    myChecksum = 0
    ID = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    
    myChecksum = checksum(header + data)
    
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = socket.htons(myChecksum)
        
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    return packet

def get_route(hostname):
    destAddr = socket.gethostbyname(hostname)
    print(f"Трассировка маршрута к {hostname} [{destAddr}]:\n")
    
    for ttl in range(1, MAX_HOPS + 1):
        for tries in range(TRIES):
            icmp = socket.getprotobyname("icmp")
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            
            mySocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            
            try:
                d = build_packet()
                mySocket.sendto(d, (destAddr, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], TIMEOUT)
                howLongInSelect = time.time() - startedSelect
                
                if not whatReady[0]:
                    print(f"{ttl:2d}  * * * Превышен интервал ожидания запроса")
                    break
                    
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                
                ihl = (recvPacket[0] & 0xF) * 4
                icmpHeader = recvPacket[ihl:ihl+8]
                type, code, checksum, pID, sequence = struct.unpack("bbHHh", icmpHeader)
                
                # доп задание: получение имени промежуточного узла
                try:
                    router_hostname, _, _ = socket.gethostbyaddr(addr[0])
                except socket.herror:
                    router_hostname = addr[0]
                
                if type == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[ihl+28:ihl+28+bytes])[0]
                    rtt = (timeReceived - timeSent) * 1000
                    print(f"{ttl:2d}  {rtt:.2f} мс  {router_hostname} ({addr[0]})")
                    break
                elif type == 3: 
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[ihl+28:ihl+28+bytes])[0]
                    rtt = (timeReceived - timeSent) * 1000
                    print(f"{ttl:2d}  {rtt:.2f} мс  {router_hostname} ({addr[0]}) [Назначение недоступно]")
                    return
                elif type == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[ihl+8:ihl+8+bytes])[0]
                    rtt = (timeReceived - timeSent) * 1000
                    print(f"{ttl:2d}  {rtt:.2f} мс  {router_hostname} ({addr[0]})")
                    return
                else:
                    print(f"{ttl:2d}  Неизвестный тип ответа: {type}")
                    break
                    
            except socket.timeout:
                print(f"{ttl:2d}  * * * Превышен интервал ожидания запроса")
                break
            finally:
                mySocket.close()
                
        if type == 0 or type == 3:
            break

if __name__ == "__main__":
    get_route("google.com")