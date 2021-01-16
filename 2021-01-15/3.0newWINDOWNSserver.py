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
PORT = 8003
IPORT = (IP0, PORT)
MAX_IP = 30


def main():#主函数
    t0 = threading.Thread(target=socketchoice, args=())

    print(" Main-Function has been loaded! Socket-Connection will starting···")

    t0.start()



def socketchoice():#线程选择函数
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(IPORT)
    sock.listen(MAX_IP)
    while True:
        server, addr = sock.accept()
        print('make connection from {0}'.format(addr))
        bathPaths = ('D:\\NJAUROBOT\\Device_01\\', 'D:\\NJAUROBOT\\Device_02\\', 'D:\\NJAUROBOT\\Device_03\\', 'D:\\NJAUROBOT\\Device_04\\', 'D:\\NJAUROBOT\\Device_05\\', 'D:\\NJAUROBOT\\Device_06\\', 'D:\\NJAUROBOT\\Device_07\\', 'D:\\NJAUROBOT\\Device_08\\', 'D:\\NJAUROBOT\\Device_09\\', 'D:\\NJAUROBOT\\Device_10\\', 'D:\\NJAUROBOT\\Device_11\\', 'D:\\NJAUROBOT\\Device_12\\')
        x = server.recv(1)
        x = int(x.decode())
        if x != 0:
            print('服务器端识别客户端%d成功'%(x))
            bathPath = bathPaths[x-1]
            thisDay = time.strftime("%Y-%m-%d", time.localtime())
            dayPath = bathPath + thisDay
            if not os.path.exists(dayPath):
                os.mkdir(dayPath)
            else:
                pass
        t1 = threading.Thread(target=servergps, args=(server,addr,dayPath,))#???,
        t1.start()


def socketline(dayPath):#负责一个打捆机的socket连接

    pass

def serverpic(server, filename, filesize,dayPath):#图片接收函数
    """
    输入：conn， addr——socket对象和地址
         filename， filesize——文件格式、文件大小
    """
    print('threading-pic is running!')
    try:
        recvd_size = 0
        fp = open(os.path.join(dayPath,str(filename)), 'wb')
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


def servergps(server,addr,dayPath):#导航接收函数
    print('threading-gps from {0} is running!',format(addr))
    while True:
        data = server.recv(BUFSIZE)
        if len(data) > 36:
            dataname = data.decode()
            try:
                with open(dayPath+'\gnssData.txt', 'a') as f:
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
            t1 = threading.Thread(target=serverpic, args=(server, dataname, filesize,dayPath))
            t1.run()#start就会一直在图片线程里面跑
            continue






if __name__ == "__main__":
    main()
