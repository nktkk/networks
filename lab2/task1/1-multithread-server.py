from socket import *
import threading

def handle_client(connectionSocket):
    try:
        message = connectionSocket.recv(1024).decode()
        if not message:
            connectionSocket.close()
            return
            
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.readlines()
        f.close()
        
        header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
        connectionSocket.send(header.encode())
        
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
            
    except IOError:
        error_response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n<h1>404 Not Found</h1>'
        connectionSocket.send(error_response.encode())
    finally:
        connectionSocket.close()

serverPort = 6789
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5) 
print(f'Многопоточный сервер запущен на порту {serverPort}...')

while True:
    connectionSocket, addr = serverSocket.accept()
    thread = threading.Thread(target=handle_client, args=(connectionSocket,))
    thread.start()