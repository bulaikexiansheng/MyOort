from Connection.OOrtRequest import ConnectState
from Connection.OOrtRequest import createRequest, connectToSever, sendRequestToServer
import argparse

parser = argparse.ArgumentParser(description="这个脚本用来向服务器发送一个工作配置文件，服务器将开启工作")
parser.add_argument("--job_path", type=str, help="工作定义的xml配置文件")
args = parser.parse_args()

xmlConfigFilePath = args.job_path
config = createRequest(xmlConfigFilePath, ConnectState.ASK_FOR_REGISTER)
connectSocket = connectToSever(config.targetIp, config.targetPort)
sendRequestToServer(config, connectSocket)

