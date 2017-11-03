import windowfile
import numpy as np
import matplotlib.pyplot as plt

A = np.array( list(windowfile.readwinsEx2( open('0.spikes', 'r'))) )

plt.plot(A[1:], np.diff(A))
plt.show()
