"""

	Name: server programme
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
# import serial # 串口通信

"""
客户端发送两个数据包，分别是txt数据和jpg数据，当检测为txt时，
调用server_gps接收gps信号并解包，在服务端读取检测到jpg时触发
启动线程，调用server_pic函数,接收完图片后关闭线程。
"""
# 初始化socket 初始化参数
BUFSIZE = 1024
IP_SERVER = ('0.0.0.0')
IP_LOCALTEST = ('127.0.0.1')
PORT = 18888
IP_PORT = (IP_SERVER, PORT)
MAX_IP_LINK = 30 # 最大并发连接数30
LABELLENGTH = struct.calcsize('32si') # 用于类型判断的标志长度
CONNECTION_LIST = [] # LIST：IP地址
CONNECTION_DT = {} # Dictioary：Socket对象

# 主函数
def main():
    t1 = threading.Thread(target=SocketSelectClient, args=(), name='SocketSelectClient')

    print("< {} > Main-Function has been loaded! Socket-Connection will starting···".format(GetLocalTime()))
    
    t1.start()

# 获取本地时间
def GetLocalTime(OutputSelection = 3):
    """
    OutputSelection Parameters:
    1 —— 1608728612.9450793
    2 —— time.struct_time(tm_year=2020, tm_mon=12, tm_mday=23, tm_hour=21, tm_min=3, tm_sec=32, tm_wday=2, tm_yday=358, tm_isdst=0)
    3 —— 2020-12-23 21:03:32
    4 —— Wed Dec 23 21:03:32 2020
    """
    try:
        if OutputSelection == 1:
            # 格式化成1608728612.9450793形式
            _localtime = time.time()
            # print ("当前时间戳为:", ticks)
        elif OutputSelection == 2:
            # 格式化成time.struct_time(tm_year=2020, tm_mon=12, tm_mday=23, tm_hour=21, tm_min=3, tm_sec=32, tm_wday=2, tm_yday=358, tm_isdst=0)
            _localtime = time.localtime(time.time())
            # print ("本地时间为 :", localtime)
        elif OutputSelection == 3:
            # 格式化成2016-03-20 11:45:39形式
            _localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        elif OutputSelection == 4:
            # 格式化成Sat Mar 28 22:24:24 2016形式
            _localtime = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
            # print (time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()))
    except NameError: 
        print("_localtime NULL!")
    else:
        return _localtime

# 进行socket初始化
def SocketLinkSet():
    # 初始化socket 并进行端口复用
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _sock.bind(IP_PORT)
    _sock.listen(MAX_IP_LINK)
    
    return _sock

# 负责一次socket连接的具体工作
def SocketLinkConnection(clientsock, clientaddress):
    while True:
        try:
            recvdata = clientsock.recv(BUFSIZE)
            # time.sleep(0.5)
            if len(recvdata) > LABELLENGTH:
                # 执行GPS接收
                ServerGps(recvdata)
            elif len(recvdata) == LABELLENGTH:
                # 执行图像接收
                ServerPic(clientsock, recvdata)
            elif not recvdata:
                raise ConnectionError
                # else:
                #     # 测试用 可去除
                #     print("< {0} > [{1}] : {2}".format(GetLocalTime(), clientaddress, recvdata.decode()))

        except ConnectionError:
            clientsock.close()
            print("< {0} > Offline-DisConnection from:{1}···".format(GetLocalTime(), clientaddress))
            _index = CONNECTION_LIST.index(clientaddress)
            CONNECTION_DT.pop(clientaddress)
            CONNECTION_LIST.pop(_index)
            # 调试时break 正常运行时去除
            break

# 管理多socket通信，并分发线程
def SocketSelectClient():
    _sock = SocketLinkSet()
    while True:
        clientsock, clientaddress = _sock.accept()
        # 对于第一次连接的IP保存记录
        if clientaddress not in CONNECTION_LIST:
            CONNECTION_LIST.append(clientaddress)
            CONNECTION_DT[clientaddress] = clientsock
            print("< {0} > New-Socket-Connection from:{1}···".format(GetLocalTime(), clientaddress))
        #在这里创建线程，就可以每次都将socket进行保持
        SocketThreading = threading.Thread(target=SocketLinkConnection, args=(clientsock, clientaddress))
        SocketThreading.start()

# 负责图像的收发
def ServerPic(clientsock, recvdata):
    """ 
    输入：conn， addr——socket对象和地址
         filename， filesize——文件格式、文件大小
    """
    # 发送字段，确认收到包头
    # server.send(('judgement receive success!').encode('utf-8'))
    filename, filesize = struct.unpack('32si', recvdata)
    filename = filename.strip(b'\00')
    filename = filename.decode()

    try:
        recvd_size = 0  # 定义已接收文件的大小
        # 存储在该脚本所在目录下面
        fp = open('./' + str(filename), 'wb')      
        # 将分批次传输的二进制流依次写入到文件
        print('0 filesize is {}'.format(filesize))
        while not recvd_size == filesize:
            if filesize - recvd_size > 1024:
                recvdata = clientsock.recv(1024)
                recvd_size += len(recvdata)
            else:
                recvdata = clientsock.recv(filesize - recvd_size)
                recvd_size += len(recvdata)
            fp.write(recvdata)
        # 清空缓存区 完成一次图片传输
        fp.flush()
        fp.close()
        # 接受完成后不用关闭clientsock

    except ConnectionResetError:
        print('图片输入错误')

# 负责GPS的收发
def ServerGps(recvdata):
    _recvdata = recvdata.decode() ### 2038：接收到图片数据
    try:
        print('收到导航信息：', _recvdata)
    except ConnectionResetError:
        print('导航信息输入错误')

# 文件路径保存！！！！！！！！！！
def SaveFilePath():# ——id负责定义文件名；——日期负责分天保存；——》》
    basePath = 'D:\\Device_01\\'
    thisDay = time.strftime("%Y-%m-%d", time.localtime())
    dayPath = basePath + thisDay
    if not os.path.exists(dayPath):
        os.mkdir(dayPath)
    else:
        pass
    return dayPath

# 日期更新判断
def DiffDaysDicide():
    pass

# 设备判断
def DiffDevicesDicide():
    pass

if __name__ == "__main__":
    main()