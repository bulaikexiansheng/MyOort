import os.path
import socket
from pprint import pprint

from Objects import ClientObject
from Objects.ClientObject import clientConstruction
from Utils.ShaTool import calculate_file_signature
from Utils.XMLTool import parseXmlFileToDict, parseXmlStringToDict


def sendFileToClient(fileName: str, clientSocket: socket):
    """
    从服务器下发文件到客户端
    :param fileName: 文件的完整路径名
    :param clientSocket: 客户端
    :return:
    """
    # with open(fileName, 'rb') as file:
    #     file_data = file.read(1024)
    #     while file_data:
    #         clientSocket.sendall(file_data)
    #         file_data = file.read(1024)
    # clientSocket.close()
    with open(fileName, "rb") as file:
        clientSocket.sendfile(file)


def sendStrContentToClient(dataContent: str, clientSocket: socket):
    """
    发送控制命令到客户端
    :param dataContent: 数据内容
    :param clientSocket: 服务器与客户端的socket
    :return: Succeed(True) or Failed(False)
    """
    clientSocket.sendall(dataContent.encode("utf-8"))


def recvDataFromSocket(src: socket, speed: int = 1024):
    """
    该函数从一个socket中获得数据
    :param src: 从一个源socket获得数据
    :param speed: 每一次获得多少个字节，默认1024
    :return:
    """
    contentStr = ""
    while True:
        line = src.recv(speed)
        if not line:
            break
        contentStr = "".join((contentStr, line.decode("utf-8")))
    return contentStr


def endSignal(flag):
    """
    学习是否结束判断
    :param flag:
    :return:
    """
    return flag


def connectToClient(ipAddress, port):
    # 创建客户端socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.bind((request.srcIp, request.srcPort))
    # 连接到服务器
    client_socket.connect((ipAddress, port))
    return client_socket


def dispatchModelToSingleClient(client, modelName, paramPath):
    """
    发送模型命令和模型参数到客户端
    :param client: 客户端
    :param modelName: 模型的名字
    :param paramPath: 参数路径
    :return:
    """
    clientSocket = connectToClient(client.getIpAddress(), client.getPort())
    # TODO: 发送一些配置信息
    sendStrContentToClient(modelName, clientSocket)
    # TODO: 发送参数文件
    sendFileToClient(paramPath, clientSocket)


def dispatchModelToClients(clients, modelName, param):
    """
    从服务器分发模型到客户端
    :param clients: 选到的客户端
    :param modelName: 任务使用到的模型
    :param param: 上一次训练得到的模型参数，初始为None
    :return:
    """
    for client in clients:
        dispatchModelToSingleClient(client, modelName, param)


class ParameterServer:
    def __init__(self, host, port):
        """
        服务器初始化
        :param port: 服务器监听的端口
        """
        # 用户管理器
        self.clientManager = ClientManager()
        # 服务器运行端口
        self.ENABLE_RUNNING = True
        # 服务器的ip地址
        self.host = host
        # 服务器监听的端口
        self.port = port
        # 创建一个socket对象
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 将socket绑定到指定的主机和端口
        self.serverSocket.bind((self.host, self.port))
        # 开始监听传入的连接,100为最大的连接数
        self.serverSocket.listen(100)

    def start(self):
        print(f"Server listening on {self.host}:{self.port}")
        while self.ENABLE_RUNNING:
            # 等待客户端连接
            client_socket, client_address = self.serverSocket.accept()
            print(f"Accepted connection from {client_address}")
            # 解析客户端发送的数据
            srcData = recvDataFromSocket(client_socket)
            dictData = parseXmlStringToDict(srcData)
            dictData['src']['ip'] = client_address[0]
            dictData['src']['port'] = client_address[1]
            # 解析客户端请求的服务，分配对应的函数
            self.requestRedirect(dictData, client_socket)

    def registerClient(self, client: ClientObject, clientSocket: socket):
        """
        新来到的客户端加入用户列表
        :return:
        """
        self.clientManager.registerFreshClient(client, clientSocket)

    def requestRedirect(self, clientRequestData: dict, clientSocket: socket):
        """
        根据客户请求数据进行重定向
        :param clientSocket: 客户端的socket
        :param clientRequestData: 客户发来的请求数据
        :return: 逻辑处理函数
        """
        if clientRequestData["request"]["type"] == "register":
            self.registerClient(clientConstruction(clientRequestData), clientSocket)
        elif clientRequestData["request"]["type"] == "job":
            self.handleJob(clientRequestData)

    def handleJob(self, jobConfig):
        """
        该函数用来处理工作
        :param jobConfig: 工作配置
        :return:
        """
        # 输出任务的相关信息
        jobName = jobConfig["job"]["job_name"]
        workerNum = jobConfig["job"]["workers"]
        dataset = jobConfig["job"]["dataset"]
        modelName = jobConfig["job"]["models"]["model"]
        print("\n==================================job submitted================================")
        print(f"jobName: {jobName}")
        print(f"workerNum: {workerNum}")
        print(f"dataset: {dataset}")
        print(f"model: {modelName}")
        # clients = self.clientManager.getCandidateClients(int(workerNum))
        clients = self.clientManager.getCandidateClients(1)
        print("\n==================================clients selected================================")
        for i, client in enumerate(clients):
            print(f"rank_{i} {client}")
        print("\n==================================dispatch model================================")
        modelName = "_".join([jobName, workerNum, dataset, modelName])
        modelName = "".join([modelName, ".pth"])
        modelPath = os.path.join("models", modelName)
        modelPath = "models/model_ds_30.pth"
        while endSignal(True):
            if not os.path.exists(modelPath):
                print("模型暂不存在")
                dispatchModelToClients(clients, modelName, None)
            else:
                print("模型已存在")
                dispatchModelToClients(clients, modelName, modelPath)
            break
        print("\n==================================wait for clients train================================")
        print("\n==================================begin================================")
        print("\n==================================end================================")


class ClientManager:
    def __init__(self):
        """
        客户端管理者，管理新到的客户端以及从可选用户中进行客户端选择
        """
        self.onlineClients = []
        self.clientSocketMap = {}

    def registerFreshClient(self, freshClient: ClientObject, freshSocket: socket):
        """
        新用户到来需要注册信息；
        :param freshClient:
        :return:
        """
        print("==================================client registered================================")
        if freshClient not in self.onlineClients:
            self.onlineClients.append(freshClient)
            self.clientSocketMap[f"{freshClient.getIpAddress()}"] = freshSocket
            print(f"{freshClient.getIpAddress()} 已注册...")
            print(f"socket list size: {self.clientSocketMap}")
        else:
            print("用户已存在...")
            try:
                peer_address = self.clientSocketMap[freshClient.getIpAddress()].getpeername()
                print(f"Peer address: {peer_address}")
            except socket.error as e:
                print(f"Error getting peer address: {e}")

    def getOnlineClients(self):
        """
        获得当前在线的用户列表
        :return:
        """
        return self.onlineClients, self.clientSocketMap

    def getCandidateClients(self, workerNum):
        """
        执行客户端选择
        :param workerNum:
        :return:
        """
        # TODO: do client select here
        if workerNum > len(self.onlineClients):
            return None
        return self.onlineClients[:workerNum]


if __name__ == '__main__':
    ps = ParameterServer('172.30.87.227', 6666)
    ps.start()
