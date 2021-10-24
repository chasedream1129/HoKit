from sys import argv
import struct
import re


def findSkin(res):
    print("Finding Skins")
    if type(res) == bytes:
        res = res.decode("utf-8")
    re_英雄代码_名字_皮肤代码 = re.compile(r"\d{3}_[a-zA-Z]+/(\d{3}0\d)/")
    re_英雄代码_名字_皮肤代码_星元 = re.compile(r"\d{3}_[a-zA-Z]+/(\d{3}0\d/\d{3})/")
    re_皮肤代码_名字 = re.compile(r"/(\d{3}0\d)_[a-z]+")

    allCode = re_英雄代码_名字_皮肤代码.findall(
        res) + re_英雄代码_名字_皮肤代码_星元.findall(res) + re_皮肤代码_名字.findall(res)
    allCode = list(set(allCode))
    allCode.sort()
    codeStr = ""
    for code in allCode:
        codeStr += code+"\n"
    return codeStr


def openDB(path):
    with open(path, "rb")as f:
        db = f.read()
    return db


def getIndexOffset(res):
    offset = 0
    indexList = []
    while True:
        findOffset = res.find(b'\xff\xff\xff\xff', offset)
        if findOffset == -1:
            break
        indexOffset = res[findOffset-4:findOffset]
        packedOffset = struct.pack('<I', findOffset-4)
        if indexOffset == packedOffset:
            indexList.append(findOffset-4)
            offset = findOffset+4
        else:
            offset = findOffset
            offset += 4
    return indexList


def getNameList(offsetList, res):
    indexList = offsetList
    nameList = []
    for offset in indexList:
        nameLen = struct.unpack("<I", res[offset+20:offset+24])[0]
        dataLen = struct.unpack("<I", res[offset+24:offset+28])[0]
        offset += 28+dataLen
        nameList.append(res[offset:offset+nameLen])
    return nameList


def writeList(path, nameList):
    text = b''
    with open(path, "wb") as f:
        for line in nameList:
            f.write(line + b'\n')


def main(dbPath, writePath):
    print("openDB")
    db = openDB(dbPath)
    print("getIndexOffset")
    indexList = getIndexOffset(db)
    print("getNameList")
    nameList = getNameList(indexList, db)
    print("writeList")
    writeList(writePath, nameList)
    with open(writePath, 'r') as f:
        resText = f.read()
    skinList = findSkin(resText)
    with open(writePath.replace('ResEntriesDB.txt', 'SkinList.txt'), 'w') as f:
        f.write(skinList)


if len(argv) == 3:
    dbPath = argv[1]
    writePath = argv[2]
    main(dbPath, writePath)
else:
    print("usage: HoK_ResLister.py dbPath writePath")
    ver = input("version:")
    main("/data/data/com.tencent.tmgp.sgame"+ver+"/files/QtsVFSCache/exportdata/ResEntriesDB.db",
         "/storage/emulated/0/git/Sga-M-E/list/ResEntriesDB.txt")
