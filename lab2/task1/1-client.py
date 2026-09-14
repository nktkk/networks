import sys
from socket import *

if len(sys.argv) != 4:
    print("Использование: python client.py <хост_сервера> <порт_сервера> <имя_файла>")
    sys.exit(1)

server_host = sys.argv[1]
server_port = int(sys.argv[2])
filename = sys.argv[3]

clientSocket = socket(AF_INET, SOCK_STREAM)

try:
    clientSocket.connect((server_host, server_port))
    
    request = f'GET /{filename} HTTP/1.1\r\nHost: {server_host}\r\n\r\n'
    clientSocket.send(request.encode())
    
    response = clientSocket.recv(4096).decode()
    print("Ответ от сервера:")
    print(response)
    
except ConnectionRefusedError:
    print(f"Ошибка: Не удалось подключиться к {server_host}:{server_port}")
except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    clientSocket.close()