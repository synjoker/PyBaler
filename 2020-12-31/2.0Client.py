#客户端融合代码（稿一）
import threading
import time
import serial
import socket
import sys
import struct
import os
import cv2

BUFSIZE = 948
IP0 = ('0.0.0.0') # 需要连接啥IP在这里修改
IP1 = ('10.49.33.32')
PORT = 18888
IPORT = (IP1, PORT)
lock = threading.Lock()

def GnssData(client):
    sergps = serial.Serial("COM7",115200, timeout=5)  # 开启com7口，波特率460800，超时5
    sergps.flushInput()  # 清空缓冲区
    serpic = serial.Serial("COM3", 9600, timeout=5)  # 开启com3口，波特率115200，超时5
    serpic.flushInput()  # 清空缓冲区
    # # 准备头文件并发送
    # filepath = 'gps'
    # fhead = struct.pack('32si', os.path.basename(filepath).encode('utf-8'), 79)
    # client.send(fhead)
    i=0
    while True:
        # print(i)

        count = serpic.inWaiting()  # 获取串口缓冲区数据
        if count != 0:
            # lock.acquire(False)
            thisDay = time.strftime("%Y-%m-%d", time.localtime())
            if os.path.exists('D:/' + str(thisDay) + '.txt'):
                pass
            else:
                f = open('D:/' + str(thisDay) + '.txt', "a+")  # a+（读+写）文件不存在就创建文件，文件存在不清空继续写
                f.write('1')
                f.flush()
            g = open('D:/' + str(thisDay) + '.txt', "r+")  # r+（读+写）文件不存在就报错，文件存在也不清空文件，而是在开头写
            b = g.readline()
            i = int(b)
            t1 = threading.Thread(target=CameraData, args=(client, i))#实列化进程
            t1.run()
            # lock.release()
            serpic.flushInput()
            count = 0
            c = int(b) + 1
            g.seek(0, 0)
            g.write(str(c))
            g.close()#重要
            continue
        count = sergps.inWaiting()  # 获取串口缓冲区数据
        if count != 0:
            # 读出串口数据，数据采用gbk编码
            recvgps = sergps.read(sergps.in_waiting).decode("gbk")
            print(recvgps)
            # if recvgps[0] != '$' or count != 79:
            #     continue
            # else:
            client.send(recvgps.encode('utf-8'))
        time.sleep(0.2)
        continue# 延时0.1秒，免得CPU出问题
        
def CameraData(client, i):
    # print('flag1')
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)# 传到256张都没问题 刚刚不小心把这一句改掉了 你补一下
    ret, frame = cap.read()
    # # 展示图片
    # cv2.imshow("capture", frame)
    # while cv2.waitKey(1) != 0:
        # 存储图片
    picname = 'camera' + str(i) + '.jpg'
    cv2.imwrite(picname, frame)
    filepath = picname



    # print('flag2')
    # 判断是否为文件
    if os.path.isfile(filepath):
        # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
        fileinfo_size = struct.calcsize('32si')
        # 定义文件头信息，包含文件名和文件大小
        fhead = struct.pack('32si', os.path.basename(filepath).encode('utf-8'), os.stat(filepath).st_size)
        # 发送文件名称与文件大小
        # print('flag2.6')
        # print(fhead)
        # time.sleep(1.5)
        client.send(fhead)  ###2038：发送投保数据，但是图片数据同时发送？？？
        # print('flag3')
        print(client.recv(BUFSIZE).decode('utf-8'))
        # print('flag3.5')
        # 将传输文件以二进制的形式分多次上传至服务器
        fp = open(filepath, 'rb')
        # print('flag4')
        while 1:
            data = fp.read(1024)
            client.send(data)
            if not data:
                print('{0} file send over...'.format(os.path.basename(filepath)))
                break
        fp.flush()
        # time.sleep(2.5)# 接收完图片之后 给予一定时间给服务器接收
        print(client.recv(BUFSIZE).decode('utf-8'))

        # 关闭当期的套接字对象
        #client.close()

def main():
    pass
    # myname = socket.getfqdn(socket.gethostname())
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(IPORT)
    #myaddr = socket.gethostbyname(myname)#本机ip
    while True:
        t0 = threading.Thread(target=GnssData, args=(client, ))#实列化进程
        t0.run()


if __name__=='__main__':
    main()