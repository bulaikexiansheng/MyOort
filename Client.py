import os
import socket
from Connection.OOrtRequest import ConnectState
from Utils.ShaTool import calculate_file_signature
from Connection.OOrtRequest import createRequest, connectToSever, sendRequestToServer


def recvDataFromServer(connectSocket: socket):
    """
    从服务器接受bytes数据
    :param connectSocket:
    :return:
    """
    dataBytes = b''
    dataRecv = connectSocket.recv(1024)
    while not dataRecv:
        dataBytes = dataBytes + dataRecv
        dataRecv = connectSocket.recv(1024)
    return dataBytes


def recvFileFromServer(connectSocket: socket, savePath):
    """
    从服务器接受文件
    :param connectSocket:
    :param savePath:
    :return:
    """
    if os.path.exists(savePath):
        os.remove(savePath)
    with open(savePath, 'ab') as file:
        file.write(recvDataFromServer(connectSocket))


# 新用户注册
xmlConfigFilePath = "client_register.xml"
config = createRequest(xmlConfigFilePath, ConnectState.ASK_FOR_REGISTER)
connectSocket = connectToSever(config.targetIp, config.targetPort)
sendRequestToServer(config, connectSocket)
# while True:
#     # 收配置
#     recvDataFromServer(connectSocket)
#     # 收文件
#     recvFileFromServer(connectSocket, "output/model.pth")
