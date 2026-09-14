import socket
import time

server_address = ('127.0.0.1', 12001)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

seq = 1
print("Отправка UDP Heartbeat... (Нажмите Ctrl+C для остановки)")

try:
    while True:
        current_time = time.time()
        message = f"{seq} {current_time}"
        
        client_socket.sendto(message.encode(), server_address)
        print(f"Отправлен пульс: seq={seq}")
        
        seq += 1
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nКлиент остановлен.")
finally:
    client_socket.close()