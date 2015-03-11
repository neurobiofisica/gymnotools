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
    while n < N:
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels = struct.unpack('qii', f.read(8+4*2))
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            yield (off, ch, np.frombuffer(f.read(samples*4), dtype=np.float32))
            n+=1
            if n >= N:
                break

def readwinsEx2(f, N=np.inf):
    n = 0
    while n < N:
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels = struct.unpack('qii', f.read(8+4*2))
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            f.read(samples*4)
        yield off

def readwinsEx3(f, N=np.inf):
    n = 0
    while n < N:
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels = struct.unpack('qii', f.read(8+4*2))
        signals = []
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            signals.append( (chid, np.frombuffer(f.read(samples*4), dtype=np.float32) ) )
            n+=1
            if n >= N:
                break
        yield (lastlen, off, samples, channels, signals)

def writewin(f, win):
    # wins = list of ( lastlen, off, samples, channels, [(chid, sig), ...] )
    f.write(struct.pack('i',win[0]))
    f.write(struct.pack('qii', win[1], win[2], win[3]))
    for ch in win[4]:
        f.write(struct.pack('i',ch[0]))
        f.write(ch[1].tostring())
        if ch[1] / w[3] != w[2]:
            print "ERROR!!"

