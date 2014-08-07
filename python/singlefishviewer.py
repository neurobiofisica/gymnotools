import re
import numpy as np
import matplotlib.pyplot as plt

NumChannels = 11
BytesPerSample = NumChannels*4
EODSamples = 128

def parsefile(f):
    expr = re.compile(r'(\d+)\s+(\d+)')
    for line in f.xreadlines():
        m = expr.match(line)
        offA = int(m.group(1))
        offB = int(m.group(2))
        yield (offA, offB)
        
def showdata(f, info):
    print(repr(info))
    offA, offB = info
    offMin, offMax = min(info), max(info)
    
    offMax += 11*EODSamples*BytesPerSample
    offMin -= 10*EODSamples*BytesPerSample
    offMin = max(0, offMin)
    rlen = offMax - offMin
    
    posA = (offA-offMin) / BytesPerSample
    posB = (offB-offMin) / BytesPerSample    
    
    f.seek(offMin)
    data = f.read(rlen)
    arr = np.frombuffer(data, dtype=np.float32)
    
    plt.clf()
    ax = None
    for ch in xrange(NumChannels):
        charr = arr[ch::NumChannels]
        if ch == 0:
            ax = plt.subplot(NumChannels, 1, 1)
        else:
            plt.subplot(NumChannels, 1, ch+1, sharex=ax)
        plt.plot(charr,'k')
        plt.axvspan(posA, posA + EODSamples, fc='r', ec='r', alpha=.5)
        plt.axvspan(posB, posB + EODSamples, fc='g', ec='g', alpha=.5)
        plt.axis([0, len(charr), -10, 10])
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
