import numpy as np
import sys

Cb = np.loadtxt(sys.argv[1], dtype=np.int)
Ce = np.loadtxt(sys.argv[2], dtype=np.int)
out = open(sys.argv[3], 'w')

for n in range(Cb.size):
    out.write('%d %d\n'%(Cb[n], Ce[n]))
    out.flush()
