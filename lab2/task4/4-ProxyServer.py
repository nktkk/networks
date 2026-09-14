from socket import *
import sys
import os
import urllib.parse

serverPort = 8888

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 

tcpSerSock.bind(('', serverPort))
tcpSerSock.listen(5)

print(f'Прокси-сервер запущен и слушает порт {serverPort}...')

cached_objects = set()

while True:
    print('Готов к обслуживанию...')
    tcpCliSock, addr = tcpSerSock.accept()
    
    try:
        message = tcpCliSock.recv(8192).decode('utf-8', errors='ignore')
        # -----------------------------------------------
        
        if not message:
            tcpCliSock.close()
            continue

        print("Запрос клиента:", message.split('\r\n')[0])
        
        try:
            url = message.split()[1]
            parsed_url = urllib.parse.urlparse(url)
            hostn = parsed_url.netloc
            path = parsed_url.path if parsed_url.path else '/'
            
            cache_filename = (hostn + path).replace('/', '_').replace(':', '_')
        except Exception as e:
            print("Ошибка парсинга URL:", e)
            tcpCliSock.send(b"HTTP/1.0 400 Bad Request\r\n\r\n")
            tcpCliSock.close()
            continue

        fileExist = False
        
        if cache_filename in cached_objects and os.path.exists(cache_filename):
            fileExist = True
        elif os.path.exists(cache_filename):
            fileExist = True
            cached_objects.add(cache_filename)

        try:
            if fileExist:
                print(f'*** ПОПАДАНИЕ В КЭШ: Читаем из {cache_filename}')
                with open(cache_filename, "rb") as f:
                    outputdata = f.readlines()
                
                tcpCliSock.send(b"HTTP/1.0 200 OK\r\n")
                tcpCliSock.send(b"Content-Type: text/html\r\n\r\n")
                for line in outputdata:
                    tcpCliSock.send(line)
                    
            else:
                print(f'*** ПРОМАХ КЭША: Запрос к веб-серверу {hostn}')
                
                c = socket(AF_INET, SOCK_STREAM)
                c.settimeout(5.0)
                
                try:
                    c.connect((hostn, 80))
                    request_to_server = f"GET {path} HTTP/1.0\r\nHost: {hostn}\r\nConnection: close\r\n\r\n"
                    c.send(request_to_server.encode())
                    
                    response_data = b""
                    while True:
                        data = c.recv(4096)
                        if not data:
                            break
                        response_data += data
                    
                    if response_data:
                        tcpCliSock.send(response_data)
                        
                        with open(cache_filename, "wb") as tmpFile:
                            tmpFile.write(response_data)
                        cached_objects.add(cache_filename)
                        print(f'Сохранено в кэш: {cache_filename}')
                    else:
                        tcpCliSock.send(b"HTTP/1.0 502 Bad Gateway\r\n\r\n")
                        
                except error as e:
                    print("Ошибка соединения с целевым сервером:", e)
                    tcpCliSock.send(b"HTTP/1.0 502 Bad Gateway\r\n\r\n")
                finally:
                    c.close()
                    
        except IOError as e:
            print("Ошибка ввода-вывода:", e)
            error_msg = b"HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1><p>File not found</p>"
            tcpCliSock.send(error_msg)
        except Exception as e:
            print("Неверный запрос:", e)
            tcpCliSock.send(b"HTTP/1.0 400 Bad Request\r\n\r\n")
            
    finally:
        tcpCliSock.close()