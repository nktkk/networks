from socket import *
import base64
import mimetypes

mailserver = 'smtp.gmail.com'
mailport = 25
sender = 'nikit4256@gmail.com'
recipient = 'nickf0934@yandex.ru'

boundary = "----=_Part_Boundary_12345"

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, mailport))
clientSocket.recv(1024)
clientSocket.send(b'HELO Alice\r\n')
clientSocket.recv(1024)
clientSocket.send(f'MAIL FROM: <{sender}>\r\n'.encode())
clientSocket.recv(1024)
clientSocket.send(f'RCPT TO: <{recipient}>\r\n'.encode())
clientSocket.recv(1024)
clientSocket.send(b'DATA\r\n')
clientSocket.recv(1024)

headers = f"From: {sender}\r\nTo: {recipient}\r\nSubject: Письмо с картинкой\r\n"
headers += f"MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=\"{boundary}\"\r\n\r\n"

text_part = f"--{boundary}\r\n"
text_part += "Content-Type: text/plain; charset=\"utf-8\"\r\n\r\n"
text_part += "Привет! Это текст письма, а ниже картинка.\r\n\r\n"

with open("image.jpg", "rb") as img_file:
    img_data = img_file.read()
    img_b64 = base64.b64encode(img_data).decode()

img_part = f"--{boundary}\r\n"
img_part += "Content-Type: image/jpeg\r\n"
img_part += "Content-Transfer-Encoding: base64\r\n"
img_part += "Content-Disposition: attachment; filename=\"image.jpg\"\r\n\r\n"
img_part += img_b64 + "\r\n\r\n"

end_boundary = f"--{boundary}--\r\n"

full_message = headers + text_part + img_part + end_boundary + ".\r\n"
clientSocket.send(full_message.encode())
clientSocket.recv(1024)

clientSocket.send(b'QUIT\r\n')
clientSocket.recv(1024)
clientSocket.close()
print("Письмо с изображением успешно отправлено!")