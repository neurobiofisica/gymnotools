import numpy as np
import sys, os

NumChannels = 7
NumValidationChannels = 2

filename = sys.argv[1]

infile = open(filename, 'rb')
filename = os.path.basename(filename)
outdata = open('%s_0' % filename, 'wb')
outval = [open('%s_%d' % (filename, i+1), 'wb') for i in xrange(NumValidationChannels)]

BuffSamples = 10000000
NumTotalChannels = NumChannels + NumValidationChannels
BuffSize = 4 * BuffSamples * NumTotalChannels

while True:
    buff = infile.read(BuffSize)
    if buff == '': break
    data = np.frombuffer(buff, dtype=np.float32)
    data = data.reshape((-1, NumTotalChannels))
    outdata.write(data[:,:NumChannels].tostring())
    for i, f in enumerate(outval):
        f.write(data[:,NumChannels+i].tostring())

infile.close()
outdata.close()
for f in outval: f.close()
