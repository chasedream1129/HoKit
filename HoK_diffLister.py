import os
import shutil
import time


def copyDir(fromPath, toPath):
    shutil.copytree(fromPath, toPath)


def getDate():
    date = time.strftime("%m-%d_%H-%M", time.localtime())
    with open("/sdcard/HoK/diff/.date", "w")as f:
        f.write(date)
    return date


def getDiffDir():
    diffDir = "/sdcard/Android/data/com.tencent.tmgp.sgame/files/iips_download/diff_extra"
    if len(os.listdir(diffDir)) == 0:
        diffDir = "/sdcard/Android/data/com.tencent.tmgp.sgamece/files/iips_download/diff_extra"
        if len(os.listdir(diffDir)) == 0:
            print("不存在diff文件!")
            diffDir = input("请输入目录(为空则退出):")
            if diffDir == "":
                exit()
    return diffDir


def getDiffFileList(path):
    fileList = []
    for name in os.listdir(path):
        if os.path.getsize(f"{path}/{name}") > 327679:
            filePath = f"{path}/{name}"
            fileList.append(filePath)
    return fileList


def parseDiffFile(diffFilePath):
    diffFile = open(diffFilePath, 'rb').read()
    QTSF = bytes("QTSF", encoding="utf8")
    QTSF_DIFF = bytes("QTSF_DIFF", encoding="utf8")
    qtsfOffset = diffFile.find(QTSF)
    qtsfCount = diffFile.count(QTSF)-1  # 减一是去掉'QTSF_DIFF'
    qtsfList = []
    if qtsfCount > 0:
        for i in range(qtsfCount):
            qtsfOffset = diffFile.find(QTSF, qtsfOffset+4)
            fileNameLen = diffFile[qtsfOffset+20:qtsfOffset+24]
            fileNameLen = int.from_bytes(fileNameLen, byteorder='little')
            fileName = str(
                diffFile[qtsfOffset+24:qtsfOffset+24+fileNameLen], encoding="utf-8")
            qtsfList.append({'name': fileName, 'offset': qtsfOffset})
    return qtsfList


def writeList(qtsfList, path):
    writeList = []
    for qtsfDict in qtsfList:
        name = qtsfDict["name"]+"\n"
        writeList.append(name)
    writeListF = writeList
    writeListF.sort()
    writeStr = "".join(writeListF)
    writeStr = writeStr.encode("utf-8")
    writeStr = writeStr
    if len(writeStr) > 0:
        with open(path, "wb") as f:
            f.write(writeStr)
            print(f"Parsed {path}")


def main():
    if not os.path.exists("/sdcard/HoK/diff/"):
        os.makedirs("/sdcard/HoK/diff/")
    date = getDate()
    diffPath = getDiffDir()
    toPath = f"/sdcard/HoK/diff/{date}/db"
    print("Copying...")
    copyDir(diffPath, toPath)
    diffList = getDiffFileList(toPath)
    os.makedirs(f"/sdcard/HoK/diff/{date}/list")
    dictData = {}
    print("Parsing...")
    for path in diffList:
        qtsfList = parseDiffFile(path)
        fileName = path.replace(toPath+"/", "")
        dictData[fileName] = {
            "fromVer": "",
            "toVer": "",
            "data": qtsfList
        }
        writePath = path.replace(".db", ".txt").replace("/db", "/list")
        writeList(qtsfList, writePath)
    return dictData


print("=====Running=====")
main()
print("=====Done=====")
