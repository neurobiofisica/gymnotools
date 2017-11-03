import sys, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

if sys.version_info.major == 3:
    xrange = range
    raw_input = input

nChan = 7
freq = 50000
winSize = int(freq * 0.5) # 0.5s
A = np.memmap(sys.argv[1], dtype='float32')

if os.path.isfile('chirps.txt') == True:
    ans = raw_input('Overwrite chirps file?')
    if ans in ['y', 'Y']:
        chirpsFile = open('chirps.txt', 'w')
    else:
        print('Appending to end of file')
        chirpsFile = open('chirps.txt', 'a')
else:
    chirpsFile = open('chirps.txt', 'w')


if os.path.isfile('without_chirps.txt') == True:
    ans = raw_input('Overwrite without_chirps file?')
    if ans in ['y', 'Y']:
        nonchirpsFile = open('without_chirps.txt', 'w')
    else:
        print('Appending to end of file')
        nonchirpsFile = open('without_chirps.txt', 'a')
else:
    nonchirpsFile = open('without_chirps.txt', 'w')

class getWindow(object):
    def __init__(self):
        self.ch = []
        for i in range(nChan):
            self.ch.append( A[i::nChan] )
        self.size = self.ch[0].size

        self.f = plt.figure(1)
        self.ax = self.f.add_subplot(111)

        self.lines = []
        for i in range(nChan):
            l, = plt.plot(range(winSize), range(winSize))
            self.lines.append(l)

        plt.xlim([0, winSize])
        plt.ylim([-10, 10+5*nChan])

        self.plotNext()

    def getNextStart(self):
        self.start = np.random.randint(self.size)
        self.start = self.start - (self.start % nChan)
        print(self.start)

    def plotNext(self):
        self.getNextStart()
        for i in range(nChan):
            data = 5*i + self.ch[i][self.start:self.start+winSize]
            self.lines[i].set_ydata( data )
        plt.draw()


    def isChirp(self, event):
        sumAbs = np.zeros(winSize)
        for i in range(nChan):
            sumAbs += np.abs(self.ch[i][self.start:self.start+winSize])
        for s in sumAbs:
            chirpsFile.write('%f '%s)
        chirpsFile.write('\n')
        chirpsFile.flush()

        self.plotNext()

    def notChirp(self, event):
        sumAbs = np.zeros(winSize)
        for i in range(nChan):
            sumAbs += np.abs(self.ch[i][self.start:self.start+winSize])
        for s in sumAbs:
            nonchirpsFile.write('%f '%s)
        nonchirpsFile.write('\n')
        nonchirpsFile.flush()

        self.plotNext()

    def skip(self, event):
        self.plotNext()

callback = getWindow()

axChirp = plt.axes([ 0.6, 0.05, 0.09, 0.075 ])
axSkip = plt.axes([ 0.7, 0.05, 0.09, 0.075 ])
axNonchirp = plt.axes([ 0.8, 0.05, 0.09, 0.075 ])

bChirp = Button(axChirp, 'Chirp')
bSkip = Button(axSkip, 'Skip')
bNonchirp = Button(axNonchirp, 'Non Chirp')

bChirp.on_clicked(callback.isChirp)
bSkip.on_clicked(callback.skip)
bNonchirp.on_clicked(callback.notChirp)

plt.show()
