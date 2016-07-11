import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sg
import windowfile
import sys

A = windowfile.readwinsEx(open(sys.argv[1]))
H = np.zeros(256)

vec_raw = np.zeros(1000000)

j=0
i=0
while(True):
    try:
        i += 1

        off, ch, sig_now = A.next()
        H += np.abs(sg.hilbert(sig_now))
        
        if i % 11 == 0:
            idx, = np.where( H > 0.2 * H.max())
            t = idx.size
            vec_raw[j] = t
            j += 1
            H.fill(0.)

            if j % 1000 == 0:
                sys.stdout.write('\r%d'%j)
                sys.stdout.flush()
    except:
        break


vec = np.zeros(j)
vec = vec_raw[:j]

print('--')
print(vec.max())

plt.plot(vec)
plt.show()
