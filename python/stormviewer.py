import re
import numpy as np
import matplotlib.pyplot as plt

NumChannels = 7
BytesPerSample = NumChannels*4

def parsefile(f):
    expr = re.compile(r'(\d+)\s*-\s*(\d+)\s*:\s*([0-9, ]+)')
    for line in f.xreadlines():
        m = expr.match(line)
        start = int(m.group(1))
        end = int(m.group(2))
        chs = [int(x.strip()) for x in m.group(3).split(',')]
        yield (start, end, chs)
        
def showdata(f, storminfo):
    print(repr(storminfo))
    start, end, chs = storminfo
    stormlen = end - start
    f.seek(start * BytesPerSample)
    data = f.read(stormlen * BytesPerSample)
    arr = np.frombuffer(data, dtype=np.float32)
    plt.clf()
    i, ax = 1, None
    for ch in chs:
        if i == 1:
            ax = plt.subplot(len(chs), 1, 1)
        else:
            plt.subplot(len(chs), 1, i, sharex=ax)
        i += 1
        plt.plot(arr[ch::NumChannels], 'g')
    plt.show()
        
def showfile(datafile, stormfile):
    for storminfo in parsefile(stormfile):
        showdata(datafile, storminfo)
        
if __name__ == '__main__':
    import sys
    datafile = open(sys.argv[1],'rb')
    stormfile = open(sys.argv[2],'rb')
    showfile(datafile, stormfile)