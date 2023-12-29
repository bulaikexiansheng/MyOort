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
    print("客户端开始监听服务器发来的信息...")
    dataRecv = connectSocket.recv(1024)
    while dataRecv:
        dataBytes = dataBytes + dataRecv
        if dataBytes.endswith(b"****"):
            dataBytes = dataBytes.replace(b"****", b"")
            # print(dataBytes)
            break
        dataRecv = connectSocket.recv(1024)
    return dataBytes


def recvFileFromServer(connectSocket: socket, savePath, saveName):
    """
    从服务器接受文件
    :param connectSocket:
    :param savePath:
    :return:
    """
    size = len(os.listdir(savePath))
    saveName = saveName.replace("*", str(size))
    savePath = os.path.join(savePath, saveName)
    print(f"文件保存在{savePath}")
    # if os.path.exists(savePath):
    #     os.remove(savePath)
    with open(savePath, 'ab') as file:
        file.write(recvDataFromServer(connectSocket))


# 新用户注册
xmlConfigFilePath = "client_register.xml"
config = createRequest(xmlConfigFilePath, ConnectState.ASK_FOR_REGISTER)
connectSocket = connectToSever(config.targetIp, config.targetPort)
sendRequestToServer(config, connectSocket)
while True:
    # 收配置
    dataBytes = recvDataFromServer(connectSocket)
    print(dataBytes.decode('utf-8'))
    # 收文件
    recvFileFromServer(connectSocket, "output", "model*.pth")
