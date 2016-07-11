import numpy as np
import matplotlib.pyplot as plt
import windowfile
import sys

chunk = 10000
NSpikes = 25

A = np.memmap( sys.argv[1], dtype=np.float32, mode='r')
H = np.memmap( sys.argv[2], dtype=np.float32, mode='r')
wins = windowfile.readwinsEx2Center( open(sys.argv[3], 'r') )

listWins = list(wins)

idxBeg = 0
while idxBeg+chunk < A.size//11:
    for i in range(11):
        plt.plot( np.arange(idxBeg,idxBeg+chunk)  ,A[i + 11*idxBeg: i + 11*(idxBeg+chunk): 11], 'k-')
    plt.plot( np.arange(idxBeg,idxBeg+chunk)  ,H[i + idxBeg: i + (idxBeg+chunk)], 'c-')
    first = next( n for n,(o,c,s) in enumerate(listWins) if o > idxBeg )
    for i in range(50):
        o, c, s = listWins[first+i]
        plt.plot([o,o], [-10,10], 'b-', alpha=0.3)
        plt.plot([o+s,o+s], [-10,10], 'b-', alpha=0.3)
        plt.plot([o+c,o+c], [-10,10], 'r-')
    plt.xlim( (idxBeg,idxBeg+chunk) )
    plt.show()
    idxBeg = idxBeg + chunk
