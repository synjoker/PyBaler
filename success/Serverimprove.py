import threading
import time
import struct
import sys
import socket
import serial

"""
客户端发送两个数据包，分别是txt数据和jpg数据，当检测为txt时，
调用server_gps接收gps信号并解包，在服务端读取检测到jpg时触发
启动线程，调用server_pic函数,接收完图片后关闭线程。
"""
# IP连接
BUFSIZE = 1024
IP0 = ('0.0.0.0')
IP1 = ('127.0.0.1')
PORT = 18888
IPORT = (IP0, PORT)
MAX_IP = 30 # 最大并发连接数30

def serverpic(server, filename, filesize):
    """ 
    输入：conn， addr——socket对象和地址
         filename， filesize——文件格式、文件大小
    """
    print('********THREAD-PIC IS RUNNING********')
    # 发送字段，确认收到包头
    # server.send(('judgement receive success!').encode('utf-8'))
    try:
        recvd_size = 0  # 定义已接收文件的大小
        # 存储在该脚本所在目录下面
        fp = open('./' + str(filename), 'wb')
        print('********PIC START RECVING********')
        

        # 将分批次传输的二进制流依次写入到文件
        print('0 filesize is {}'.format(filesize))
        while not recvd_size == filesize:
            if filesize - recvd_size > 1024:
                data = server.recv(1024)
                recvd_size += len(data)
                # print('1 recvdsize is {}'.format(recvd_size))
            else:
                data = server.recv(filesize - recvd_size)
                # print('2 Ending recvdata are {}'.format(data))
                recvd_size += len(data)
                # print('2 Ending recvdsize is {}'.format(recvd_size))
            fp.write(data)

        # 清空缓存区 完成一次图片传输
        fp.flush()
        fp.close()
        print('********PIC END RECVING********')
        server.send(('pic end receive').encode('utf-8'))
        time.sleep(2.5)
        # 接受完成后不用关闭conn
    except ConnectionResetError:
        print('图片输入错误')

def servergps(server):
    print('********THREAD-GPS IS RUNNING********')
    while True:
        data = server.recv(BUFSIZE)
        time.sleep(0.5)
        print(data)
        if len(data) > 36:
            # print('flag1')
            # 解码导航字符串
            dataname = data.decode() ### 2038：接收到图片数据
            try:
                print('收到导航信息：', dataname)
            except ConnectionResetError:
                print('导航信息输入错误')
        elif len(data) == 36:
            # print('flag2')
            # 调用解包程序并进行解码图片
            server.send(('data end receive').encode('utf-8'))
            dataname, filesize = struct.unpack('32si', data)
            dataname = dataname.strip(b'\00')
            dataname = dataname.decode()
            # print(dataname)
            # print('file  name is {0}, filesize if {1}'.format(str(dataname), filesize))
            # t1 = threading.Thread(target=serverpic, args=(server, dataname, filesize))
            # t1.run()
            serverpic(server, dataname, filesize)
            continue

        # if dataname[0] != '$':
        #     print('file  name is {0}, filesize if {1}'.format(str(dataname), filesize))
        #     t1 = threading.Thread(target=serverpic, args=(server, dataname, filesize))
        #     t1.run()
        #     continue
        # elif dataname[0] == '$':
        #     try:
        #         print('收到导航信息：', dataname)
        #     except ConnectionResetError:
        #         print('导航信息输入错误')

def judgementip(server, addr):
    """
    server:32si
    """
    # 收到请求后的回复
    # server.send('Hi, Welcome to the server!'.encode('utf-8'))
    fileinfo_size = struct.calcsize('32si')
    buf = server.recv(fileinfo_size)
    if buf:
        filename, filesize = struct.unpack('32si', buf)
        fn = filename.strip(b'\00')
        fn = fn.decode()
        print('file  name is {0}, filesize if {1}'.format(str(fn), filesize))

        if fn[-3:] == 'jpg':
            return str(fn), filesize

        return str(''), filesize

def judgementfile(fn):
    """
    server:32si
    """
    # 收到请求后的回复
    # server.send('Hi, Welcome to the server!'.encode('utf-8'))
    buf = fn
    if buf:
        filename, filesize = struct.unpack('32si', buf)
        fn = filename.strip(b'\00')
        fn = fn.decode()
        print('file  name is {0}, filesize if {1}'.format(str(fn), filesize))

        if fn[-3:] == 'jpg':
            return str(fn), filesize

        return str(''), filesize

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(IPORT)
    sock.listen(MAX_IP)
    #接受TCP连接并返回（conn,address）,其中conn是新的套接字对象，可以用来接收和发送数据。address是连接客户端的地址。
    server, addr = sock.accept()
    print('make connection from {0}'.format(addr))
    while True: 
        t0 = threading.Thread(target=servergps, args=(server, ))
        t0.run()  
                
if __name__ == "__main__":
    main()