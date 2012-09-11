import re
import numpy as np
import matplotlib.pyplot as plt

NumChannels = 7
BytesPerSample = NumChannels*4
EODSamples = 128

def parsefile(f):
    expr = re.compile(r'([ABab])\s*(\d+)')
    for line in f.xreadlines():
        m = expr.match(line)
        fish = m.group(1).upper()
        off = int(m.group(2))
        yield (fish, off)
        
def showdata(f, info):
    print(repr(info))
    fish, off = info
    
    f.seek(off)
    data = f.read(EODSamples * BytesPerSample)
    arr = np.frombuffer(data, dtype=np.float32)
    
    plt.clf()
    ax = None
    for ch in xrange(NumChannels):
        charr = arr[ch::NumChannels]
        if ch == 0:
            ax = plt.subplot(NumChannels, 1, 1)
        else:
            plt.subplot(NumChannels, 1, ch+1, sharex=ax)
        plt.plot(charr, 'r' if fish=='A' else 'g')
        plt.ylabel('ch%d'%ch)
        
    plt.show()
        
def showfile(datafile, singlefishfile):
    for info in parsefile(singlefishfile):
        showdata(datafile, info)
        
if __name__ == '__main__':
    import sys
    datafile = open(sys.argv[1],'rb')
    singlefishfile = open(sys.argv[2],'rb')
    showfile(datafile, singlefishfile)