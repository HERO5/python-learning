from socket import *
from time import ctime
import sys
sys.path.append("../chinese_article_analysis")
sys.path.append("../pyserial")
from article_analysis import ArticleAnalysis
from pyserial import SerialPort

stop = b"0"  # 将0转换为ASCII码方便发送
start = b"1"  # 同理
fast = b"4"  # 将0转换为ASCII码方便发送
slow = b"5"  # 同理
serialPort = "COM3"  # 串口
baudRate = 9600  # 波特率
HOST = ''
PORT = 9999
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)   #创建套接字
tcpSerSock.bind(ADDR)   #绑定IP和端口
tcpSerSock.listen(5)    #监听端口，最多5人排队
article_analysis = ArticleAnalysis()
mSerial = SerialPort(serialPort, baudRate)

while True:
    print('waiting for connection...')
    tcpCliSock, addr = tcpSerSock.accept()    #建立连接
    print('...connected from:', addr)

    while True:
        data = tcpCliSock.recv(BUFSIZ)
        if not data:
            break
        cmd = int.from_bytes(data,byteorder='big',signed=False)
        print("cmd", cmd)
        if cmd == 48:
            mSerial.send_data(stop)
            continue
        if cmd == 49:
            mSerial.send_data(start)
            continue
        text = str(data, encoding='utf-8')
        print("text: ", text)

        result = ArticleAnalysis.string_semantic_analysis(text, "dut", "bsa_algorithm")
        score = result['score']
        print("score: ", score)

        if score > 0:
            mSerial.send_data(fast)
        elif score < 0:
            mSerial.send_data(slow)
        # tcpCliSock.send(content.encode("utf-8"))

    tcpCliSock.close()

tcpSerSock.close()