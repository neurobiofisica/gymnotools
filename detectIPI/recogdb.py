import bsddb3.db as bsd
from bsddb3 import _DBWithCursor

import struct
import numpy as np

# TODO: read from external file
NumChannels = 11

def compare_fcn(a, b):
    if a and b:
        decA = struct.unpack('=q',a)
        decB = struct.unpack('=q',b)
        
        if decA < decB:
            return -1
        elif decA > decB:
            return 1
        else:
            return 0
    return 0

def verifyKey(db,k):
    if not (isinstance(k,int) or isinstance(k,str)):
        print "key must be an integer or an 8 byte (64-bit) binary string\n"
        return None

    # string len verification
    elif isinstance(k,str):
        if len(k) != 8:
            print "The string must be an 8 byte (64-bit) size\n"
            return None
        key = k

    # Convert number to binary representation
    elif isinstance(k,int):
        key = struct.pack('q',k)

    if db.has_key(key) == False:
        print "key not found\n"
        return None

    return key


def openDB(filename, mode):
    if mode not in ('r','w','rw','c','n'):
        print "mude must be one of 'r','w','rw','c','n'\n"
        return None

    flags = 0
    if mode == 'r':
        flags = bsd.DB_RDONLY
    elif mode == 'rw':
        flags = 0
    elif mode == 'w':
        flags =  bsd.DB_CREATE
    elif mode == 'c':
        flags =  bsd.DB_CREATE
    elif mode == 'n':
        flags = dbsd.DB_CREATE

    flags |= bsd.DB_THREAD

    env = bsd.DBEnv()
    env.open('.', bsd.DB_PRIVATE | bsd.DB_CREATE | bsd.DB_THREAD | bsd.DB_INIT_LOCK | bsd.DB_INIT_MPOOL)

    db = bsd.DB(env)
    db.set_bt_compare(compare_fcn)
    db.open(filename, bsd.DB_BTREE, flags, 0)

    return _DBWithCursor(db)

def parseDBHeader(copy):
    bindata = copy
    presentFish, direction, distA, distB, distAB, flags, correctedPos, svm, pairsvm, probA, probB = struct.unpack('=iifffiqiqff', bindata[:52])
    svm = chr(svm)
    return (presentFish, direction, distA, distB, distAB, flags, correctedPos, svm, pairsvm, probA, probB, bindata[:52])

def binarizeDBHeader(tup):
    presentFish, direction, distA, distB, distAB, flags, correctedPos, svm, pairsvm, probA, probB = tup
    svm = ord(svm)
    return struct.pack('=iifffiqiqff',presentFish, direction, distA, distB, distAB, flags, correctedPos, svm, pairsvm, probA, probB)

def fishwin(bindata):
    off, size = struct.unpack('ii', bindata[:8])
    bindata = bindata[8:]
    dataitems = NumChannels * size
    datalen = dataitems * 4
    data = np.frombuffer(bindata[:datalen], dtype=np.float32)
    bindata = bindata[datalen:]
    data = data.reshape((NumChannels, size))
    return (off, data), bindata

def fishrec(tup):
    off, bindata = tup
    off, = struct.unpack('q', off)
    presentFish, direction, distA, distB, distAB, flags, correctedPos, svm, pairsvm, probA, probB, spkdata = parseDBHeader(bindata)
    #print '%d\t%d\t%f\t%f\t%f\t%d\t%c\t%d\t%f\t%f\n'%(off,presentFish,distA,distB,distAB,flags,svm,pairsvm,probA,probB)
    fishwins = {}
    if presentFish & 1:
        fishwins['A'], spkdata = fishwin(spkdata)
    if presentFish & 2:
        fishwins['B'], spkdata = fishwin(spkdata)
    return off, direction, distA, distB, distAB, flags, svm, pairsvm, probA, probB, fishwins

def readHeaderEntry(db,k):
    key = verifyKey(db,k)
    if key is None:
        return None

    try:
        tup = db.set_location(key)
    except bsd.DBNotFoundError:
        print 'set_location failed\n'
        return None

    
    off, bindata = tup
    off = struct.unpack('q',off)
    presentFish, direction, distA, distB, distAB, flags, correctedPos, svm, pairsvm, probA, probB, spkdata = parseDBHeader(bindata)

    return (off, (presentFish, direction, distA, distB, distAB, flags, correctedPos, svm, pairsvm, probA, probB))

def updateHeaderEntry(db, k, field, data):
    key = verifyKey(db,k)
    if key is None:
        return None

    svmPos = 7

    # it is not possible to modify channel flags or svm cause (will be modified to 'm')
    dic = {'presentFish': 0,
            'direction': 1,
            'distA': 2,
            'distB': 3,
            'distAB': 4,
            'correctedPos': 6,
            'pairsvm': 8,
            'probA': 9,
            'probB': 10,
        }
    if field not in dic.keys():
        print 'You can only modify one of the fields: ' + str(dic.keys()) + '\n'
        return None
    

    raw = readHeaderEntry(db,key)
    if raw is None:
        return None

    off, old_data = raw
    new_data = list(old_data)

    new_data[ dic[field] ] = data
    #Change svm to 'm'
    new_data[ svmPos ] = 'm'

    new_data = binarizeDBHeader(new_data)

    db.update( [(key, new_data), ] )
    db.sync()
