import socket
import sys
from pprint import pformat
from Utils.XMLTool import parseXmlFileToDict, parseXmlStringToDict
from Utils.FileUtil import readFileToString


class ConnectState:
    # 新客户端连接服务器
    ASK_FOR_REGISTER = 0
    # 客户端离线
    ASK_FOR_OVER = 1
    # 客户端提交训练好的参数到服务器
    SUBMIT_FILE_FROM_CLIENT_TO_SERVER = 2
    # 服务器下发模型和训练参数到客户端
    DOWNLOAD_FILE_FROM_SERVER_TO_CLIENT = 3


class OOrtRequest:
    def __init__(self):
        """
        客户端和服务器之间沟通的数据包
        """
        self.flag = None
        self.bodyContent = None
        self.targetIp = None
        self.targetPort = None
        self.srcIp = None
        self.srcPort = None

    def setBody(self, bodyContent: str):
        self.bodyContent = bodyContent
        return self

    def setFlag(self, flag):
        """
        设置Request包的类型
        :param flag: ConnectionState.X
        :return:
        """
        if not self.flag:
            self.flag = flag

    def getFlag(self, flag):
        return self.flag

    def body(self):
        """
        传输主体内容
        :return:
        """
        return self.bodyContent


def createRequest(xmlConfigFile, flag):
    """
    客户端加入服务器
    :param flag: 注册还是参数聚合,ConnectionState.X
    :param xmlConfigFile: ；
    :return:
    """
    # 配置文件
    config = readFileToString(xmlConfigFile)
    # print(config)
    configDict = parseXmlStringToDict(config)
    # 设置
    request = OOrtRequest().setBody(config)
    # # 设置标志位,是注册还是参数聚合
    # request.setFlag(flag)
    # 这个包发给谁
    request.targetIp = configDict["target"]["ip"]
    request.targetPort = int(configDict["target"]["port"])
    # 这个包是谁发的
    request.srcIp = socket.gethostbyname(socket.gethostname())
    request.srcPort = int(configDict["src"]["port"])
    # 修改内容中的ip地址
    # request.bodyContent['src']['ip'] = request.srcIp
    # print(request.body())
    return request


def connectToSever(targetIp, targetPort):
    # 创建客户端socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.bind((request.srcIp, request.srcPort))
    # 连接到服务器
    client_socket.connect((targetIp, targetPort))
    return client_socket


def sendRequestToServer(request, client_socket):
    client_socket.sendall(f"{request.body()}".encode("utf-8"))