import socket
import os
import sys
import struct
import time
import select
import statistics

ICMP_ECHO_REQUEST = 8

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

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = time.time() - startedSelect
        
        if not whatReady[0]:
            return "Превышен интервал ожидания запроса"
            
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        ihl = (recPacket[0] & 0xF) * 4 
        icmpHeader = recPacket[ihl:ihl+8]
        type, code, checksum, pID, sequence = struct.unpack("bbHHh", icmpHeader)
        
        if type == 3:
            if code == 0: return "Сеть назначения недоступна"
            elif code == 1: return "Хост назначения недоступен"
            elif code == 3: return "Порт недоступен"
            else: return f"Назначение недоступно (Код {code})"
        elif type == 11:
            return "Время жизни пакета истекло"
            
        if pID == ID:
            bytes = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[ihl+8:ihl+8+bytes])[0]
            delay = timeReceived - timeSent
            return delay * 1000 

        timeLeft -= howLongInSelect
        if timeLeft <= 0:
            return "Превышен интервал ожидания запроса"

def sendOnePing(mySocket, destAddr, ID, seq):
    myChecksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    data = struct.pack("d", time.time())
    
    myChecksum = checksum(header + data)
    
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = socket.htons(myChecksum)
        
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))

def doOnePing(destAddr, timeout, ID, seq):
    icmp = socket.getprotobyname("icmp")
    
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    
    sendOnePing(mySocket, destAddr, ID, seq)
    delay = receiveOnePing(mySocket, ID, timeout, destAddr)
    mySocket.close()
    return delay

def ping(host, timeout=1):
    dest = socket.gethostbyname(host)
    print(f"Пингуем {dest} используя Python:")
    print("")
    
    myID = os.getpid() & 0xFFFF
    rtt_list = []
    sent_count = 0
    lost_count = 0
    
    try:
        # доп задание: отправка 4 пакетов для сбора статистики
        for i in range(4): 
            sent_count += 1
            delay = doOnePing(dest, timeout, myID, i+1)
            
            if isinstance(delay, float):
                rtt_list.append(delay)
                print(f"Ответ от {dest}: время={delay:.2f}мс")
            else:
                lost_count += 1
                print(f"{delay}")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
        
    # доп задание: вывод статистики
    print("\n--- Статистика пинга ---")
    print(f"Пакетов: отправлено = {sent_count}, получено = {sent_count - lost_count}, "
          f"потеряно = {lost_count} ({lost_count/sent_count*100:.1f}% потерь)")
    if rtt_list:
        print(f"Приблизительное время приема-передачи в мс:")
        print(f"    Минимальное = {min(rtt_list):.2f} мс, "
              f"Среднее = {statistics.mean(rtt_list):.2f} мс, "
              f"Максимальное = {max(rtt_list):.2f} мс")

if __name__ == "__main__":
    ping("8.8.8.8") 