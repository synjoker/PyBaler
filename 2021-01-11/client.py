"""

	Name: client programme
	Copyright: NJAU-ROBOT
	Author: Hu Bin; Shao Yuning;
	Date: 11/01/21 16:35
	Description:  

"""
import threading # 多线程运行
import time # 时间戳
import calendar # 日历
import struct # 封包解包
import sys # 系统库
import socket # socket通信
import serial # 串口通信
import cv2 # 相机调用

import os # 图像传输时使用

# 初始化socket 初始化参数
BUFSIZE = 1024
IP_LOCALTEST = ('127.0.0.1')
IP_CLIENT = ('10.49.32.18') # 需要连接啥IP在这里修改
PORT = 18888
IP_PORT = (IP_LOCALTEST, PORT)
global PHOTO_ID = 0

NULL = 0

# 主函数
def main():
    t0 = threading.Thread(target=ClientConnectSocket, args=(), name='ClientConnectSocket')#实列化进程
    t0.start()

# GPS串口管理
def ClientGnss(clientsock, clientgps):
    # 读出串口数据，数据编码传输
    recvgps = clientgps.read(clientgps.in_waiting)
    clientsock.send(recvgps.encode('utf-8'))
    # 定义数据的间隔
    time.sleep(0.2)

# 相机串口管理
def ClientCamera(clientsock, PHOTO_ID):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    ret, frame = cap.read()
    # 文件保存并传输机制
    picname = 'camera' + str(PHOTO_ID) + '.jpg'
    cv2.imwrite(picname, frame)
    filepath = picname
    # 判断是否为文件
    if os.path.isfile(filepath):
        # 定义定义文件信息。32s表示文件名为32bytes长，l表示一个int或log文件类型，在此为文件大小
        fileinfo_size = struct.calcsize('32si')
        # 定义文件头信息，包含文件名和文件大小
        fhead = struct.pack('32si', os.path.basename(filepath).encode('utf-8'), os.stat(filepath).st_size)
        # 发送文件名称与文件大小
        clientsock.send(fhead)

        # 将传输文件以二进制的形式分多次上传至服务器
        fp = open(filepath, 'rb')
        while 1:
            data = fp.read(1024)
            clientsock.send(data)
            if not data:
                # print('{0} file send over...'.format(os.path.basename(filepath)))
                break
        fp.flush()

# 初始化socket
def ClientLinkSet():
    _client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _client.connect(IP_PORT)
    
    return _client

# 设置端口、波特率、延迟时间
def InputInitialization():
    _cligps = serial.Serial("COM7",115200, timeout=5)  # 开启com7口，波特率460800，超时5
    _cligps.flushInput()  # 清空缓冲区
    _clipic = serial.Serial("COM3", 115200, timeout=5)  # 开启com3口，波特率115200，超时5
    _clipic.flushInput()
    
    return _cligps, _clipic

# 管理socket连接主机，并管理串口通信
def ClientConnectSocket():
    clientsock = ClientLinkSet()
    cligps, clipic = InputInitialization()
    while True:
        
        COUNT = NULL
        # 获取串口缓冲区数据
        COUNT = clipic.inWaiting()
        if COUNT != 0:
            ClientCamera(clientsock, PHOTO_ID)
            PHOTO_ID += 1
            continue
        
        # 获取串口缓冲区数据
        COUNT = cligps.inWaiting()
        if COUNT != 0:
            ClientGnss(clientsock, cligps)
            continue
        
if __name__=='__main__':
    main()