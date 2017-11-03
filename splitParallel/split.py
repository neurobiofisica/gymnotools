#!/usr/env python

import numpy as np
import sys

nproc = 8
nchan = 7

A = np.memmap(sys.argv[1], mode='r', dtype=np.float32)
tamChunk = (A.size // nchan) // nproc

for i in range(nproc-1):
    B = np.memmap('%d.f32'%i, mode='w+', dtype=np.float32, shape=(tamChunk*nchan, ))
    B[:] = A[i*tamChunk*nchan:(i+1)*tamChunk*nchan]

finalTam = tamChunk + ( (A.size // nchan) % nproc )
B = np.memmap('%d.f32'%(nproc-1), mode='w+', dtype=np.float32, shape=(finalTam*nchan, ))
B[:] = A[(nproc-1)*tamChunk*nchan:]
