import socket
import time
from datetime import datetime

server_address = ('127.0.0.1', 12000)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client_socket.settimeout(1.0) 

total_pings = 10
rtt_list = []
lost_packets = 0

print(f"Начинаем пингование {server_address[0]}...")

for i in range(1, total_pings + 1):
    current_time = datetime.now().strftime("%H:%M:%S")
    message = f"Ping {i} {current_time}"
    
    send_time = time.time()
    client_socket.sendto(message.encode(), server_address)
    
    try:
        data, server = client_socket.recvfrom(1024)
        recv_time = time.time()
        
        rtt = recv_time - send_time
        rtt_list.append(rtt)
        
        print(f"Ответ от {server[0]}: {data.decode()} | RTT: {rtt*1000:.2f} мс")
        
    except socket.timeout:
        lost_packets += 1
        print(f"Запрос {i}: Request timed out")
        
    time.sleep(0.5) 

print("\nСтатистика пинга:")
packet_loss_percent = (lost_packets / total_pings) * 100
print(f"Пакетов: Отправлено = {total_pings}, Получено = {total_pings - lost_packets}, "
      f"Потеряно = {lost_packets} ({packet_loss_percent:.1f}% потерь)")

if rtt_list:
    min_rtt = min(rtt_list) * 1000
    max_rtt = max(rtt_list) * 1000
    avg_rtt = (sum(rtt_list) / len(rtt_list)) * 1000
    print(f"Примерное время приема-передачи в мс:")
    print(f" - Минимальное = {min_rtt:.2f}мс, Максимальное = {max_rtt:.2f}мс, Среднее = {avg_rtt:.2f}мс")
else:
    print("Ни один пакет не был получен, расчет RTT невозможен.")

client_socket.close()