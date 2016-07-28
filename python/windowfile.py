import struct
import numpy as np
import sys

if sys.version_info.major == 3:
    xrange=range

# Verificar se lastLen esta em bytes
class winFile:
    def __init__(self, f):
        self.f = f
        self.lastLen, self.off, self.samples, self.channels, self.sigs, self.center = self.readWin()
        self.nowLen = (4+8+4+4+4) + self.channels*4*(1 + self.samples)
        self.f.seek(0)
        self.beg = True

    def readWin(self):
        raw = self.f.read(4+8+4+4+4)
        if raw == '':
            return None
        try: ##############################################################
            lastLen, off, samples, channels, center = struct.unpack('=iqiii', raw)
        except struct.error:
            return None
        sigs = {}
        for ch in range(channels):
            chid, = struct.unpack('i', self.f.read(4))
            win = np.frombuffer(self.f.read(samples*4), dtype=np.float32)
            sigs.update( {chid: win} )
        return lastLen, off, samples, channels, center, sigs

    def nextWin(self):
        self.beg = False
        ret = self.readWin()
        if ret == None:
            return None
        self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs = ret
        self.nowLen = (4+8+4+4+4) + self.channels*4*(1 + self.samples)
        return self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs

    def prevWin(self):
        if self.beg == True:
            return None
        self.f.seek(self.f.tell() - self.lastLen)
        self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs = self.readWin()
        self.nowLen = (4+8+4+4+4) + self.channels*4*(1 + self.samples)
        self.f.seek(self.f.tell() - self.nowLen)
        if self.f.tell() == 0:
            self.beg = True
        return self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs

    def beg(self):
        self.f.seek(0)
        self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs = self.readWin()
        self.nowLen = (4+8+4+4+4) + self.channels*4*(1 + self.samples)
        self.f.seek(0)
        self.beg = True

    def end(self):
        while self.nextWin() != None:
            pass
        self.beg = False


def readwins(f, N=np.inf):
    n = 0
    wins = []
    while n < N:
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels, center = struct.unpack('qiii', f.read(8+4*3))
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
        off, samples, channels, center = struct.unpack('qiii', f.read(8+4*3))
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            yield (off, ch, np.frombuffer(f.read(samples*4), dtype=np.float32))
            n+=1
            if n >= N:
                break


def readwinsExAllCh(f, N=np.inf):
    n = 0
    while n < N:
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels, center = struct.unpack('qiii', f.read(8+4*3))
        sigs = {}
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            sigs.update( {chid: np.frombuffer(f.read(samples*4), dtype=np.float32)} )
            n+=1
            if n >= N:
                break
        yield (off, samples, sigs)


def readwinsEx2(f, N=np.inf):
    n = 0
    while n < N:
        n+=1
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels, center = struct.unpack('qiii', f.read(8+4*3))
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            f.read(samples*4)
        yield off

def readwinsEx2Center(f, N=np.inf):
    n = 0
    while n < N:
        n+=1
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels, center = struct.unpack('qiii', f.read(8+4*3))
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            f.read(samples*4)
        yield off, center, samples

def readwinsEx3(f, N=np.inf):
    n = 0
    while n < N:
        lastlenRaw = f.read(4)
        if lastlenRaw == '':
            break
        lastlen, = struct.unpack('i', lastlenRaw)
        off, samples, channels, center = struct.unpack('qiii', f.read(8+4*3))
        signals = []
        for ch in xrange(channels):
            chid, = struct.unpack('i', f.read(4))
            signals.append( (chid, np.frombuffer(f.read(samples*4), dtype=np.float32) ) )
            n+=1
            if n >= N:
                break
        yield (lastlen, off, samples, channels, signals)

def writewin(f, win):
    # wins = list of ( lastlen, off, samples, channels, center [(chid, sig), ...] )
    if sys.version_info.major == 2 or True:
        f.write(struct.pack('i',win[0]))
        f.write(struct.pack('qiii', win[1], win[2], win[3], win[4]))
        for ch in win[5]:
            f.write(struct.pack('i',ch[0]))
            f.write(ch[1].tostring())
    elif sys.version_info.major == 3:
        f.write(struct.pack('i',win[0]).decode())
        f.write(struct.pack('qiii', win[1], win[2], win[3], win[4]).decode())
        for ch in win[5]:
            f.write(struct.pack('i',ch[0]).decode())
            f.write(ch[1].tostring())
