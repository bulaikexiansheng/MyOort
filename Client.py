import os
import socket
from Utils.ShaTool import calculate_file_signature

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

# 文件保存路径
file_path = 'output/model_ds_30.pth'
if os.path.exists(file_path):
    os.remove(file_path)
# 接收文件内容
while True:
    file_data = client_socket.recv(1024)
    if not file_data:
        break
    with open(file_path, 'ab') as file:
        file.write(file_data)
# 计算文件的哈希值
print(calculate_file_signature(file_path))
print(calculate_file_signature(file_path))

print(f"Received from server doned")

# 关闭客户端socket
client_socket.close()
