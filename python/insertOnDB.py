import numpy as np
import recogdb
import sys

freq = 45454.545454
winSize = 512
NChan = 10

db = recogdb.openDB(sys.argv[1], 'rw')
presentFish = int(sys.argv[2])
t = [int(x) for x in sys.argv[3].split('.')]
t = 60*60*t[0] + 60*t[1] + t[2] + t[3]/10000.

key = int(t*freq)
print(key)

sigs = [np.zeros(winSize) for i in range(NChan)]

if presentFish == 1:
    recogdb.writeEntry(db, key, presentFish, 1, \
                            0, 1<<30, 1<<30, \
                            0, \
                            key, -1, \
                            'm', -1, \
                            1.0, 0.0, \
                            sigs)
elif presentFish == 2:
    recogdb.writeEntry(db, key, presentFish, 1, \
                            1<<30, 0, 1<<30, \
                            0, \
                            -1, key, \
                            'm', -1, \
                            0.0, 1.0, \
                            sigs)
else:
    print('Please insert single fish and then edit later')
