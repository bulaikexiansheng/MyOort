import socket
from Objects import ClientObject
from Utils.ShaTool import calculate_file_signature


def transferFileToClient(fileName: str, clientSocket: socket):
    """
    从服务器下发文件到客户端
    :param fileName: 文件的完整路径名
    :param clientSocket: 客户端
    :return:
    """
    # 打开文件并读取内容
    with open(fileName, 'rb') as file:
        while True:
            file_data = file.read()
            if not file_data:
                break
            clientSocket.send(file_data)

    # 发送文件内容给客户端
    clientSocket.sendall(file_data)

class ParameterServer:
    def __init__(self, host, port):
        """
        服务器初始化
        :param port: 服务器监听的端口
        """
        # 用户队列
        self.registeredClients = list()
        # 服务器运行端口
        self.ENABLE_RUNNING = True
        # 服务器监听的端口
        self.port = port
        # 创建一个socket对象
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 将socket绑定到指定的主机和端口
        self.serverSocket.bind((host, port))
        # 开始监听传入的连接,100为最大的连接数
        self.serverSocket.listen(100)
        print(f"Server listening on {host}:{port}")

    def start(self):
        while self.ENABLE_RUNNING:
            # 等待客户端连接
            client_socket, client_address = self.serverSocket.accept()
            print(f"Accepted connection from {client_address}")
            # 计算文件的哈希值
            print(calculate_file_signature("input/model_ds_30.pth"))
            print(calculate_file_signature("input/model_ds_30.pth"))
            transferFileToClient("input/model_ds_30.pth", client_socket)
            # 关闭客户端连接
            client_socket.close()
            break

    def registerClient(self, client: ClientObject):
        """
        新来到的客户端加入用户列表
        :return:
        """
        self.registeredClients.append(client)




if __name__ == '__main__':
    ps = ParameterServer('127.0.0.1', 6666)
    ps.start()
