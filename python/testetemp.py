import numpy as np
import matplotlib.pyplot as plt
import windowfile

A = windowfile.readwinsEx3(open('/ssd/15o03000_cut_h.spikes', 'r'))

while(True):
    l, o, s, ch, w = A.next()
    for c in range(11):
        plt.plot(w[c][1])
    plt.title('%d %d'%(o,s))
    plt.show()
