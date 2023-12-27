import socket

# 服务器的主机和端口
host = '127.0.0.1'
port = 6666

# 创建客户端socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接到服务器
client_socket.connect((host, port))

# # 发送一些测试数据
# message = "Hello, Server!"
# client_socket.sendall(message.encode())

# 接收文件内容
file_data = client_socket.recv(1024)

# 文件保存路径
file_path = 'fileReceived.txt'

# 将接收到的文件内容写入本地文件
with open(file_path, 'wb') as file:
    file.write(file_data)

print(f"Received from server doned")

# 关闭客户端socket
client_socket.close()
