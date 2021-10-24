# only tested in arrch64 Android device(root).
import os
import re
import struct


def getSgamePid():
    psMsg = os.popen("ps -e|grep sgame").read()
    if "sgamece\n" in psMsg:
        psPattern = "sgamece$"
        gameVer = "sgamece"
        if "sgame\n" in psMsg:
            gameVersion = input("体验服与正式服同时运行，是正式服吗？(y/n,默认y):")
            if gameVersion == "" or gameVersion == "y" or gameVersion == "Y":
                psPattern = "sgame$"
                gameVer = "sgame"
            if gameVersion == "n" or gameVersion == "N":
                psPattern = "sgamece$"
                gameVer = "sgamece"
    else:
        if "sgame\n" in psMsg:
            psPattern = "sgame$"
            gameVer = "sgame"
    try:
        print(gameVer)
    except UnboundLocalError:
        print("sgame未运行!")
        exit()
    psMsg = psMsg.splitlines()
    for i in psMsg:
        if re.search(psPattern, i) != None:
            pid = re.split(r"[ ]+", i)[1]
            print(f"Pid={pid}")
    return pid


def getIndexAdd():
    with open(f"/proc/{pid}/maps", "r") as f:
        mapMsg = f.read().splitlines()
    for i in range(len(mapMsg)):
        if "libGameCore" in mapMsg[i] and "rw-p" in mapMsg[i]:
            if "anon:.bss" in mapMsg[i+1]:
                pointerAdd = mapMsg[i+1]
                bssStart = int(pointerAdd.split("-")[0], 16)
                bssEnd = int(pointerAdd.split("-")[1].split(" ")[0], 16)
                pointerAdd = int(pointerAdd.split("-")[0], 16)
                addOffset = getPointerOffset(bssStart, bssEnd)
                pointerAdd += addOffset
                print(f"pointerAdd={hex(pointerAdd)}\naddOffset={hex(addOffset)}")
    try:
        return pointerAdd
    except UnboundLocalError:
        print("sgame未加载")
        exit()


def getMemData(start, end):
    with open(f"/proc/{pid}/mem", 'rb', 0) as mem:
        mem.seek(start)
        try:
            return mem.read(end-start)
        except BaseException:
            print("内存获取失败")


def getPointerOffset(bssStart, bssEnd):
    data = getMemData(bssStart, bssEnd)
    offset = data.find(b"\xFF\xFF\xF0\xFF\xF0\x0F\x00\x00") + 8
    return offset


def unpackBytes(bytes, type):
    if type == "D":
        rule = "<I"
    elif type == "Q":
        rule = "<Q"
    word = struct.unpack(rule, bytes)[0]
    return word


def getWord(start, type):
    if type == "D":
        len = 4
    elif type == "Q":
        len = 8
    data = getMemData(start, start + len)
    word = unpackBytes(data, type)
    return word


def getIndexAdds(indexAdd, indexLen):
    adds = []
    for i in range(indexLen - 1):
        textPointerAdd = indexAdd + i * 16
        textLen = getWord(textPointerAdd+12, "D")
        textStart = getWord(textPointerAdd, "Q")
        textEnd = textStart + textLen
        dict = {'id': i, 'start': textStart, 'end': textEnd}
        adds.append(dict)
    return adds


def parseTextData(data):
    textList = []
    i = 0
    global textLen
    textLen = 0
    while i < len(data):
        reMatch = re.search(
            bytes("[\x00-\xff]{4}\x01\x00\x00\x00", "utf-8"), data[i:i+textLen+8192])
        if reMatch != None:
            i = reMatch.start() + i
            textLen = data[i:i+4]
            textLen = unpackBytes(textLen, "D")
            i += 8
            textData = data[i:i+textLen].decode("utf-8")
            i += textLen
            textList.append(textData)
        else:
            print("parseTextData Done")
            break
    return textList


def main():
    global pid
    pid = getSgamePid()
    pointerAdd = getIndexAdd()
    indexLen = getWord(pointerAdd+20, "D")
    pointer = getWord(pointerAdd, "Q")
    adds = getIndexAdds(pointer, indexLen)
    print("getIndexAdds Done")
    print("Geting Data")
    textData = b''
    for i in adds:
        data = getMemData(i["start"], i["end"])
        textData += data
    print("Get Data Done")
    textList = parseTextData(textData)
    print("Writing")
    with open("/storage/emulated/0/git/Sga-M-E/list/textDumped.txt", "w")as f:
        for i in textList:
            f.write(f"⊙{i}∅\n")


print("=====Running=====")
main()
print("=====Done=====")
