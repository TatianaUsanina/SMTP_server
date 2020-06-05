import socket
import ssl
import base64
import configparser
import mime

PORT = 465
SERVER = 'smtp.yandex.ru'

user_name = ''
targets = ''
password = ''
subject = ''
files = []


def create_config(subject, files, recv_addr):
    config = configparser.ConfigParser()
    config['settings'] = {"subject" : subject,
                          'files' : files,
                          'recipient addresses' : recv_addr}

    with open('data\config.ini', 'w') as f:
        config.write(f)

    return config

def read_message():
    with open('data/letter.txt', 'r', encoding='utf-8') as f:
        return '\n'.join(f.readlines())

def read_file(file):
    with open(file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def create_message():
    head = ""
    head += "From: " + user_name + '\n'
    head += "To: " + targets + '\n'
    head += "Subject: " + subject + '\n'
    head += "MIME-version: 1.0" + '\n'

    bound = "bound12343244323"

    head += 'Content-Type: multipart/mixed; boundary="' + bound + '"' + '\n'
    head += '\n'
    letter_type = mime.Types.of('data/letter.txt')[0]
    body = ''
    body += '--' + bound + '\n'
    body += 'Content-Transfer-Encoding: 8bit' + "; charset=utf-8" + '\n'
    body += 'Content-Type: '+ letter_type.content_type + '\n' + '\n'
    body += read_message() + '\n'
    for file in files:
        type = mime.Types.of(file)[0]
        body += '--' + bound + '\n'
        body += 'Content-Transfer-Encoding: ' + type.encoding + '\n'
        body += 'Content-Type: ' + type.content_type + '\n' + '\n'
        body += read_file(file) + '\n'
    body += '--' + bound + '--' + '\n'
    body += '.' + '\n'

    return head + body


def request(socket, request):
    socket.send((request + '\n').encode())
    recv_data = socket.recv(65535).decode()
    return recv_data


if __name__== '__main__':
    user_name = input("Логин: ")
    password = input('Пароль: ')
    targets = input('Введите адрес(а) получателя(ей): ')
    subject = input('Тема письма: ')
    files = input('Введите файлы для вложения: ')

    config = create_config(subject, files, targets)

    files = config.get('settings', 'files').split()
    subject = config.get('settings', 'subject')
    targets = config.get("settings", 'recipient addresses')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((SERVER, PORT))
        client = ssl.wrap_socket(client)
        print(client.recv(1024))
        print(request(client, 'EHLO ' + user_name))
        base64_login = base64.b64encode(user_name.encode()).decode()
        base64_password = base64.b64encode(password.encode()).decode()
        print(request(client, 'AUTH LOGIN'))
        print(request(client, base64_login))
        print(request(client, base64_password))
        print(request(client, 'MAIL From:' + user_name))
        for target in targets.split():
            print(request(client, "RCPT TO:" + target))
        print(request(client, 'DATA'))
        print(request(client, create_message()))



