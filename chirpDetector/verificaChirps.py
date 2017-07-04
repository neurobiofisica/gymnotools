import numpy as np
import matplotlib.pyplot as plt
import sys

freq = 50000.
nchan = 7
margem = int(0.1*freq)

A = np.memmap(sys.argv[1], dtype=np.float32)
Cb, Ce = np.loadtxt(sys.argv[2], unpack=True, dtype=np.int)

for nc in range(Cb.size):
    plt.figure(1, figsize=(18,18))
    for i in range(nchan):
        S = A[i + (Cb[nc] - margem)*nchan : i + (Ce[nc] + margem)*nchan : nchan].copy()
        X = np.linspace(Cb[nc]-margem,Ce[nc]+margem,S.size) / freq
        plt.plot(X, 5*i + S)
    plt.show()
