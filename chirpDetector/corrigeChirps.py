import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import sys,os

sys.path.append( os.path.abspath('..') )
from read_param import *
# import NChan, freq, winSize

arredor = int(0.1*freq)

chirps = np.loadtxt(sys.argv[1])
f = open(sys.argv[1]+'_corr', 'w')
S = np.memmap(sys.argv[2], mode='r', dtype=np.float32)

class Geral(object):
    def __init__(self, outputfile):
        self.f = outputfile

    def carregaDados(self, beg, end):
        self.beg = beg
        self.end = end

    def isChirp(self, event):
        self.f.write('%d %d\n'%(self.beg, self.end))
        self.f.flush()
        plt.close()

    def notChirp(self, event):
        plt.close()
        
callback = Geral(f)

l,c = chirps.shape
for n,(beg,end) in enumerate(chirps):
    fig = plt.figure(1, figsize=(26,14))

    callback.carregaDados(beg, end)

    for i in range(NChan):
        plt.plot(S[i + NChan*(beg-arredor): i + NChan*(end+arredor): NChan])
    plt.title('%d - %f%%'%(n, (100.*n)/l) )

    axNo = plt.axes([0.8, 0.05, 0.1, 0.075])
    axYes = plt.axes([0.91, 0.05, 0.1, 0.075])
    bNo = Button(axNo, 'not Chirp')
    bYes = Button(axYes, 'is Chirp')
    bNo.on_clicked(callback.notChirp)
    bYes.on_clicked(callback.isChirp)

    plt.show()

f.close()
