import struct
import numpy as np

def readwins(f, N=np.inf):
    n = 0
    wins = []
    while n < N:
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels = struct.unpack('qii', f.read(8+4*2))
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            wins.append(np.frombuffer(f.read(samples*4), dtype=np.float32))
            n+=1
            if n >= N:
                break
    return np.vstack(wins)

def readwinsEx(f, N=np.inf):
    n = 0
    wins = []
    while n < N:
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels = struct.unpack('qii', f.read(8+4*2))
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            wins.append((off, ch, np.frombuffer(f.read(samples*4), dtype=np.float32)))
            n+=1
            if n >= N:
                break
    return wins
