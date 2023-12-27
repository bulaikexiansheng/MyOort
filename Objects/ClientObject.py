class ClientObject:
    def __init__(self, ipAddress, port):
        self.port = port
        self.ipAddress = ipAddress

    def getPort(self):
        return self.port

    def getIpAddress(self):
        return self.ipAddress

