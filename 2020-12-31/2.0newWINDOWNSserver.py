# -*- coding:utf-8 -*-
import threading
import time
import struct
import sys
import socket
import os

"""
客户端发送两个数据包，分别是txt数据和jpg数据，当检测为txt时，
调用server_gps接收gps信号并解包，在服务端读取检测到jpg时触发
启动线程，调用server_pic函数,接收完图片后关闭线程。
"""
BUFSIZE = 948
IP0 = ('0.0.0.0')
IP1 = ('127.0.0.1')
PORT = 8003
IPORT = (IP0, PORT)
MAX_IP = 30

def filePath():
    basePath = 'D:\\Device_01\\'
    thisDay = time.strftime("%Y-%m-%d", time.localtime())
    dayPath = basePath + thisDay
    if not os.path.exists(dayPath):
        os.mkdir(dayPath)
    else:
        pass
    return dayPath

def serverpic(server, filename, filesize):
    """
    输入：conn， addr——socket对象和地址
         filename， filesize——文件格式、文件大小
    """
    print('threading-pic is running!')
    try:
        recvd_size = 0
        fp = open(os.path.join(filePath(),str(filename)), 'wb')
        print('pic start receiving...')
        print('0 filesize is {}'.format(filesize))
        while not recvd_size == filesize:
            if filesize - recvd_size > 1024:
                data = server.recv(1024)
                recvd_size += len(data)
            else:
                data = server.recv(filesize - recvd_size)
                recvd_size += len(data)
            fp.write(data)
        fp.flush()
        fp.close()
        print('pic end receive')
        server.send(('pic end receive').encode('utf-8'))
    except ConnectionResetError:
        print('图片输入错误')


def servergps(server):
    print('threading-gps is running!')
    while True:
        data = server.recv(BUFSIZE)
        if len(data) > 36:
            dataname = data.decode()
            try:
                with open(filePath()+'\gnssData.txt', 'a') as f:
                    print(dataname)
                    f.write(dataname)
                    f.close()
            except ConnectionResetError:
                print("导航信息错误")
        elif len(data) == 36:
            server.send(('data end receive').encode('utf-8'))
            dataname, filesize = struct.unpack('32si', data)
            dataname = dataname.strip(b'\00')
            dataname = dataname.decode()
            print('file  name is {0}, filesize if {1}'.format(str(dataname), filesize))
            t1 = threading.Thread(target=serverpic, args=(server, dataname, filesize))
            t1.run()
            continue


def judgementip(server, addr):
    """
    server:32si
    """
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
    server, addr = sock.accept()
    print('make connection from {0}'.format(addr))
    while True:
        t0 = threading.Thread(target=servergps, args=(server,))
        t0.run()


if __name__ == "__main__":
    main()
