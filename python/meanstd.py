import sys
import numpy as np
a = np.loadtxt(sys.argv[1])
print repr((a.mean(), a.std()))