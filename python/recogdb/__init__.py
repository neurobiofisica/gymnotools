import sys

import bsddb3.db as bsd
import bsddb3
from bsddb3 import _DBWithCursor

import struct
import numpy as np

###############
# CUIDADO!!! Quando adicionar campo no DB, deve-se alterar o dicionario dicFields E a funcao binarizeDBHeader (struct.pack nao aceita tuplas!)


# TODO: read from external file
NumChannels = 11

dicFields = {'presentFish': 0,
        'direction': 1,
        'distA': 2,
        'distB': 3,
        'distAB': 4,
        'flags': 5,
        'correctedPosA': 6,
        'correctedPosB': 7,
        'svm': 8,
        'pairsvm': 9,
        'probA': 10,
        'probB': 11,
}

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
    if sys.version_info.major == 3:
        tp = bytes
    else:
        tp = str

    if not (isinstance(k,int) or isinstance(k,tp)):
        sys.stderr.write("key must be an integer or an 8 byte (64-bit) binary string\n")
        sys.stderr.flush()
        return None

    # string len verification
    elif isinstance(k,tp):
        if len(k) != 8:
            sys.stderr.write("The string must be an 8 byte (64-bit) size\n")
            sys.stderr.flush()
            return None
        key = k

    # Convert number to binary representation
    elif isinstance(k,int):
        key = struct.pack('q',k)

    if db.has_key(key) == False:
        #sys.stderr.write( "key not found\n")
        #sys.stderr.flush()
        return None

    return key


def openDB(filename, mode):
    if mode not in ('r','w','rw','c','n'):
        sys.stderr.write( "mude must be one of 'r','w','rw','c','n'\n")
        sys.stderr.flush()
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
        flags = bsd.DB_CREATE

    flags |= bsd.DB_THREAD

    env = bsd.DBEnv()
    env.set_lk_detect(bsd.DB_LOCK_DEFAULT)
    env.open('.', bsd.DB_PRIVATE | bsd.DB_CREATE | bsd.DB_THREAD | bsd.DB_INIT_LOCK | bsd.DB_INIT_MPOOL)

    db = bsd.DB(env)
    db.set_bt_compare(compare_fcn)
    db.open(filename, bsd.DB_BTREE, flags, 0o666)

    return _DBWithCursor(db)

def parseDBHeader(bindata):
    size = struct.calcsize('=iifffiqqiqff')

    read_data = list(struct.unpack('=iifffiqqiqff', bindata[:size]))
    read_data[ dicFields['svm'] ] = chr( read_data[ dicFields['svm'] ])
    read_data.append(bindata[size:])
    read_data = tuple(read_data)
    return read_data

def binarizeDBHeader(tup):
    presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB = tup
    svm = ord(svm)
    return struct.pack('=iifffiqqiqff',presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB)

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
    read_data = parseDBHeader(bindata)
    #spkdata = read_data[-1]
    presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB, spkdata = read_data #parseDBHeader(bindata)
    #print( '%d\t%d\t%f\t%f\t%f\t%d\t%c\t%d\t%f\t%f\n'%(off,presentFish,distA,distB,distAB,flags,svm,pairsvm,probA,probB))
    fishwins = {}
    if presentFish & 1:
        fishwins['A'], spkdata = fishwin(spkdata)
    if presentFish & 2:
        fishwins['B'], spkdata = fishwin(spkdata)
    return off, \
            read_data[ dicFields['direction'] ], \
            read_data[ dicFields['distA'] ], \
            read_data[ dicFields['distB'] ], \
            read_data[ dicFields['distAB'] ], \
            read_data[ dicFields['flags'] ], \
            read_data[ dicFields['svm'] ], \
            read_data[ dicFields['pairsvm'] ], \
            read_data[ dicFields['probA'] ], \
            read_data[ dicFields['probB'] ], \
            fishwins

def delete(db, k):
    key = verifyKey(db, k)
    if key is None:
        return None

    try: 
        del db[key]
    except:
        sys.stderr.write('pop failed\n')
        sys.stderr.flush()
        return None

def readHeaderEntry(db,k):
    key = verifyKey(db,k)
    if key is None:
        return None

    try:
        tup = db.set_location(key)
    except bsd.DBNotFoundError:
        sys.stderr.write( 'set_location failed\n')
        sys.stderr.flush()
        return None

    
    off, bindata = tup
    off, = struct.unpack('q',off)
    read_data = parseDBHeader(bindata)
    spkdata = read_data[-1]
    read_data = read_data[:-1]

    return (off, read_data, spkdata)

def get_location(db,k):
    off, bindata = db.set_location(struct.pack('=q',k))
    off, = struct.unpack('=q', off)
    read_data = parseDBHeader(bindata)
    
    return (off, read_data)

def getNSamples(db, k):
    key = struct.pack('=q', k)
    if not db.has_key(key):
        return None
    
    off, bindata = db.set_location(key)
    read_data = parseDBHeader(bindata)
    spkdata = read_data[-1]
    off2, size = struct.unpack('ii', spkdata[:8])
    
    return size

def readOff(tup):
    return struct.unpack('=q', tup[0])[0]

def getNearest(db, direction, k, fish, overlap=True):
    key = struct.pack('=q',k)
    if not db.has_key(key):
        return None
    if direction not in [-1, 1]:
        return None
    if fish not in [1, 2]:
        return None
    
    if overlap == True:
        values = [fish, 3]
    else:
        values = [fish]
    
    db.set_location(key)
    fishNow = -1
    while fishNow not in values:
        if direction == -1:
            off, bindata = db.previous()
        else:
            off, bindata = db.next()
        read_data = parseDBHeader(bindata)
        fishNow = read_data[ dicFields['presentFish'] ]
    
    off = struct.unpack('=q', off)[0]
    return (off, read_data)

def getNearestSVM(db, direction, k):
    key = struct.pack('=q',k)
    if not db.has_key(key):
        sys.stderr.write('key not found')
        sys.stderr.flush()
        return None
    if direction not in [-1, 1]:
        sys.stderr.write('direction must be 1 or -1')
        sys.stderr.flush()
        return None
    
    db.set_location(key)
    
    # Walk twice on the first step
    if direction == -1:
        off, bindata = db.previous()
    else:
        off, bindata = db.next()
        
    svm = 'X'
    while svm not in ['s','v']:
        if direction == -1:
            try:
                off, bindata = db.previous()
            except bsddb3._pybsddb.DBNotFoundError:
                return (None, None)
        else:
            try:
                off, bindata = db.next()
            except bsddb3._pybsddb.DBNotFoundError:
                return (None, None)
        read_data = parseDBHeader(bindata)
        svm = read_data[ dicFields['svm'] ]
    
    off = struct.unpack('=q', off)[0]
    return (off, read_data)

def updateHeaderEntry(db, k, field, data, change_svm=True, sync=True):
    key = verifyKey(db,k)
    if key is None:
        return None

    # It is not possible to modify the flags field
    dic = dicFields.copy()
    dic.pop('flags')
    if field not in dic.keys():
        sys.stderr.write('You can only modify one of the fields: ' + str(dic.keys()) + '\n')
        sys.stderr.flush()
        return None
    
    raw = readHeaderEntry(db,key)
    if raw is None:
        return None

    off, old_data, spkdata = raw
    new_data = list(old_data)

    new_data[ dic[field] ] = data
    #Change svm to 'm'
    if change_svm == True and field != 'svm':
        new_data[ dicFields['svm'] ] = 'm'

    new_data = binarizeDBHeader(new_data) + spkdata

    db.update( [(key, new_data), ] )
    if sync == True:
        db.sync()

def writeEntry(db, k, presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB, signals, sync=True):

    key = struct.pack('=q',k)
    headerdata = binarizeDBHeader( (presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB) )
    if type(signals) is str:
        spkdata = signals
    else:
        spkdata = struct.pack('ii', 0, signals[0].size) #0 is the offset for that fish
        for sig in signals:
            spkdata += sig.astype('float32').tostring()
    data = headerdata + spkdata
        
    db.update( [(key, data), ] )
    if sync == True:
        db.sync()
