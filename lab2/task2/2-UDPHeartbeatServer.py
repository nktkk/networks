import socket
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 12001)) 
print("UDP Heartbeat Server запущен на порту 12001...")

last_seq = 0
last_time = time.time()
timeout_threshold = 5.0 

while True:
    server_socket.settimeout(timeout_threshold)
    try:
        message, address = server_socket.recvfrom(1024)
        current_time = time.time()
        
        msg_str = message.decode()
        parts = msg_str.split()
        seq = int(parts[0])
        client_timestamp = float(parts[1])
        
        if last_seq != 0 and seq != last_seq + 1:
            print(f"Обнаружена потеря пакетов! Ожидался seq {last_seq + 1}, получен {seq}")
            
        delay = current_time - client_timestamp
        print(f"✓ Получен пульс: seq={seq}, задержка={delay:.3f} сек")
        
        last_seq = seq
        last_time = current_time
        
    except socket.timeout:
        print(f"Ошибка: Клиент не отвечает! Пульс отсутствует более {timeout_threshold} сек. ")
        last_seq = 0 