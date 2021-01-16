import os
import time

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
    print(FD_TIME)

    return FD_TIME
    # os.chdir(FD)
    # 6. 在当前路径修改文件
    # fp = open(FD_TIME + '/' + str(clientid)+'.txt', 'wb')


