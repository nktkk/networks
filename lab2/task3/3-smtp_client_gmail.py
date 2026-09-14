from socket import *
import ssl
import base64

msg = "\r\n Я люблю компьютерные сети!"
endmsg = "\r\n.\r\n"

mailserver = 'smtp.gmail.com'
mailport = 587

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, mailport))

recv = clientSocket.recv(1024).decode()
print(recv)

heloCommand = 'EHLO Alice\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)

clientSocket.send(b'STARTTLS\r\n')
recv_tls = clientSocket.recv(1024).decode()
print("STARTTLS ответ:", recv_tls)

context = ssl.create_default_context()
secure_socket = context.wrap_socket(clientSocket, server_hostname=mailserver)

secure_socket.send(b'EHLO Alice\r\n')
recv2 = secure_socket.recv(1024).decode()
print(recv2)

secure_socket.send(b'AUTH LOGIN\r\n')
secure_socket.recv(1024)

email_b64 = base64.b64encode(b"nikit4256@gmail.com").decode() + "\r\n"
pass_b64 = base64.b64encode(b"12345678").decode() + "\r\n"

secure_socket.send(email_b64.encode())
secure_socket.recv(1024)
secure_socket.send(pass_b64.encode())
auth_resp = secure_socket.recv(1024).decode()
print("Auth response:", auth_resp)

secure_socket.send(b'MAIL FROM: <nikit4256@gmail.com>\r\n')
secure_socket.recv(1024)

secure_socket.send(b'RCPT TO: <nickf0934@yandex.ru>\r\n')
secure_socket.recv(1024)

secure_socket.send(b'DATA\r\n')
secure_socket.recv(1024)

full_msg = 'From: nikit4256@gmail.com\r\nTo: nickf0934@yandex.ru\r\nSubject: TLS Test\r\n' + msg
secure_socket.send(full_msg.encode())
secure_socket.send(endmsg.encode())
secure_socket.recv(1024)

secure_socket.send(b'QUIT\r\n')
secure_socket.recv(1024)

secure_socket.close()