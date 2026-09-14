from socket import *

# Порт, на котором будет работать сервер
serverPort = 6789
serverSocket = socket(AF_INET, SOCK_STREAM) # Подготавливаем сокет сервера

# Начало вставки
# Привязываем сокет к адресу и порту, начинаем прослушивание
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
# Конец вставки

print(f'Сервер запущен и слушает порт {serverPort}...')

while True: # Устанавливаем соединение
    print('Готов к обслуживанию...')
    
    # Начало вставки
    connectionSocket, addr = serverSocket.accept()
    # Конец вставки
    
    try:
        # Начало вставки
        message = connectionSocket.recv(1024).decode()
        # Конец вставки
        
        if not message:
            connectionSocket.close()
            continue

        filename = message.split()[1]
        f = open(filename[1:])
        
        # Начало вставки
        outputdata = f.readlines()
        f.close()
        # Конец вставки
        
        # Начало вставки
        header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
        connectionSocket.send(header.encode())
        # Конец вставки
        
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
            
        connectionSocket.close()
        
    except IOError:
        # Начало вставки
        error_response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n<h1>404 Not Found</h1><p>Запрашиваемый файл не найден.</p>'
        connectionSocket.send(error_response.encode())
        # Конец вставки
        
        # Начало вставки
        connectionSocket.close()
        # Конец вставки

serverSocket.close()