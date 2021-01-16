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
import os # 管理文件路径
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
IP_PORT = (IP_LOCALTEST, PORT)
MAX_IP_LINK = 30 # 最大并发连接数30
LABELLENGTH = struct.calcsize('32si') # 用于类型判断的标志长度

"""
客户机记录（修改）
改进：
1. 新建一个txt文件专门保存这三个量
2. 服务器接收连接时，首先进行认证，在txt文件里查找信息
3. 如果有，则发送“device existence”
   如果没有，则发送“no device”
"""
CONNECTION_LIST = [] # LIST:IP地址
CONNECTION_DT = {} # Dictioary：Socket对象
CONNECTION_ID = [] # LIST:ID号

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


def CreateSavePath(clientid):
    FD = './'+str(clientid)
    # 1. 可以得到当前日期
    _localtime = time.strftime("%Y-%m-%d", time.localtime())
    # print(_localtime)
    # print(time.localtime().tm_mday)
    # _localtime = '2021-01-13'
    # print(_localtime)
    # 2. 获取当前路径
    # 3. 按照设备id创建路径
    if not os.path.exists(FD):
        os.mkdir(FD)
    # 4. 更改当前路径
    # 5. 监督日期变化，创造日期文件夹
    # os.chdir('./'+clientid)
    # print(os.getcwd())
    FD_TIME = FD + '/' +str(_localtime)
    if not os.path.exists(FD_TIME):
        os.mkdir(FD_TIME)
    # print(FD_TIME)

    return FD_TIME

# 负责一次socket连接的具体工作
def SocketLinkConnection(clientsock, clientaddress, clientid):
    while True:
        try:
            recvdata = clientsock.recv(BUFSIZE)
            # time.sleep(0.5)
            if len(recvdata) > LABELLENGTH:
                # 执行GPS接收
                ServerGps(recvdata, clientid)
            elif len(recvdata) == LABELLENGTH:
                # 执行图像接收
                ServerPic(clientsock, recvdata, clientid)
            elif not recvdata:
                raise ConnectionError
                # else:
                #     # 测试用 可去除
                #     print("< {0} > [{1}] : {2}".format(GetLocalTime(), clientaddress, recvdata.decode()))

        except ConnectionError:
            clientsock.close()
            print("< {0} > Offline-DisConnection from:{1}···".format(GetLocalTime(), clientid))
            _index = CONNECTION_LIST.index(clientaddress)
            CONNECTION_DT.pop(clientaddress)
            CONNECTION_LIST.pop(_index)
            # 调试时break 正常运行时去除
            break

def IdAuthentication(signal):
    signal = 0
    if signal in CONNECTION_DT:
        client_id = (signal + )
    pass


# 管理多socket通信，并分发线程
def SocketSelectClient():
    _sock = SocketLinkSet()
    while True:
        clientsock, clientaddress = _sock.accept()

        """
        认证程序：
        接收：接收客户端本地口令“device X”，至服务器txt文件查找对应名称
        输出：（成功）接收服务器“device existence”
            （失败）接收服务器“no device”
        返回：client id
        """
        # 对于第一次连接的IP保存记录
        if clientaddress not in CONNECTION_LIST:
            CONNECTION_LIST.append(clientaddress)
            CONNECTION_ID.append('JSTCDKJ'+str(len(CONNECTION_ID)+1))
            CONNECTION_DT[clientaddress] = clientsock
            # # 显示打捆机id
            # CONNECTION_ID[CONNECTION_LIST.index(clientaddress)]
            print("< {0} > New-Socket-Connection from:{1}···".format(GetLocalTime(), CONNECTION_ID[CONNECTION_LIST.index(clientaddress)]))
        clientid = CONNECTION_ID[CONNECTION_LIST.index(clientaddress)]
        #在这里创建线程，就可以每次都将socket进行保持
        SocketThreading = threading.Thread(target=SocketLinkConnection, args=(clientsock, clientaddress, clientid))
        SocketThreading.start()

# 负责图像的收发
def ServerPic(clientsock, recvdata, clientid):
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
        PathBaseDay = CreateSavePath(clientid)
        fp = open(PathBaseDay + '/' + str(filename), 'wb')      
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
def ServerGps(recvdata, clientid):
    _recvdata = recvdata.decode() ### 2038：接收到图片数据
    PathBaseDay = CreateSavePath(clientid)
    
    try:
        FP = open(PathBaseDay + '/' + str(clientid)+'.txt', 'a')
        # _recvdata = _recvdata + '\n'
        FP.write(_recvdata)
        # FP.close()
        # print('收到导航信息：', _recvdata)
    except ConnectionResetError:
        print('导航信息输入错误')

# 文件路径保存！！！！！！！！！！
# def SaveFilePath(clientid):# ——id负责定义文件名；——日期负责分天保存；——》》
#     basePath = 'D:/Device_'+clientid+'/'
#     thisDay = time.strftime("%Y-%m-%d", time.localtime())
#     dayPath = basePath + thisDay
#     if not os.path.exists(dayPath):
#         os.mkdir(dayPath)
#     else:
#         pass
#     return dayPath

# 日期更新判断
def DiffDaysDicide():
    pass

# 设备判断
def DiffDevicesDicide():
    pass

def OutputConnectionList():
    # 全输入到一个txt
    CONNECTION_LIST = [] # LIST:IP地址
    CONNECTION_DT = {} # Dictioary：Socket对象
    CONNECTION_ID = [] # LIST:ID号
    pass

if __name__ == "__main__":
    main()