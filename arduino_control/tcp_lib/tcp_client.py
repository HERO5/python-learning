from socket import *

class TcpClient:
    host = ''
    port = 0
    buf_size = 0
    addr = None
    tcpCliSock = None

    def __init__(self, host='127.0.0.1', port=9999, buf_size=1024):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.addr = (host, port)
        self.tcpCliSock = socket(AF_INET, SOCK_STREAM)

    def connect(self):
        self.tcpCliSock.connect(self.addr)

    def close(self):
        self.tcpCliSock.close()

    def send(self, data):
        if not data:
            return
        # self.connect()
        self.tcpCliSock.send(data.encode('UTF-8'))
        # self.close()

if __name__ == '__main__':
    tcpClient = TcpClient(host='192.168.43.192', port=80)
    tcpClient.send('hello')
