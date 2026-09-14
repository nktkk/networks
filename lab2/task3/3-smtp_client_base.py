from socket import *

msg = "\r\n Я люблю компьютерные сети!"
endmsg = "\r\n.\r\n"

mailserver = 'smtp.example.com' 
mailport = 25

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, mailport))

recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('Код 220 от сервера не получен.')

heloCommand = 'HELO Alice\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('Код 250 от сервера не получен.')

mailFromCommand = 'MAIL FROM: <sender@example.com>\r\n'
clientSocket.send(mailFromCommand.encode())
recv2 = clientSocket.recv(1024).decode()
print(recv2)

rcptToCommand = 'RCPT TO: <recipient@example.com>\r\n'
clientSocket.send(rcptToCommand.encode())
recv3 = clientSocket.recv(1024).decode()
print(recv3)

dataCommand = 'DATA\r\n'
clientSocket.send(dataCommand.encode())
recv4 = clientSocket.recv(1024).decode()
print(recv4)

full_msg = 'From: sender@example.com\r\nTo: recipient@example.com\r\nSubject: Test SMTP\r\n' + msg
clientSocket.send(full_msg.encode())

clientSocket.send(endmsg.encode())
recv5 = clientSocket.recv(1024).decode()
print(recv5)

quitCommand = 'QUIT\r\n'
clientSocket.send(quitCommand.encode())
recv6 = clientSocket.recv(1024).decode()
print(recv6)

clientSocket.close()