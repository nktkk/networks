import random
from socket import *

# Создаем UDP-сокет
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Связываем порт 12000 с сокетом сервера
serverSocket.bind(('', 12000))

print("UDP Pinger Server запущен на порту 12000...")

while True:
    rand = random.randint(0, 10)
    
    message, address = serverSocket.recvfrom(1024)
    
    message_str = message.decode().upper()
    
    if rand < 4:
        print(f"[Симуляция] Пакет потерян. Ответ не отправлен.")
        continue
        
    print(f"Отправка ответа клиенту {address}")
    serverSocket.sendto(message_str.encode(), address)