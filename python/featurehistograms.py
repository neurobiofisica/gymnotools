import sys
import numpy as np
import matplotlib.pyplot as plt
import windowfile

# | awk '{print $4" "$2 }' | sort

A = windowfile.readwins(open(sys.argv[1]))
B = windowfile.readwins(open(sys.argv[2]))

assert(A.shape[1] == B.shape[1])

for i in xrange(A.shape[1]):
    plt.clf()
    pdf, bins, patches = plt.hist((A[:,i],B[:,i]), bins=50, normed=True)
    
    minpdf = np.min(np.vstack(pdf), axis=0)
    overlap = np.sum(minpdf * np.diff(bins))
    print('feature %4d overlap: %.10f' % (i, overlap))
    sys.stdout.flush()
    plt.savefig('out/fea%04d.png'%i)