

def readFileToString(filePath):
    fileContent = ""
    with open(filePath, "rb") as file:
        while True:
            line = file.readline()
            if not line:
                break
            fileContent = "".join([fileContent, line.decode("utf-8")])
    return fileContent