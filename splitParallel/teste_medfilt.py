import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
import scipy.signal
import sys

loc = 2210530 - 100000

medfiltsize= 0.0010

hmin = 0.250
freq = 50000.
tol = int(0.0005*freq)
nchan = 7

winSize = 50000
kern_medfilt = int(0.001*freq)

A = np.memmap('2.f32', dtype=np.float32, mode='r')

def gmean(arr, kernel_size=3):
    tam = arr.size
    out = np.array( [ np.prod(arr[max(0,n):min(n+kernel_size,tam)])**(1./kernel_size) for n in range(-kernel_size//2,tam+kernel_size) ] )
    return out[kernel_size//2:tam+kernel_size//2]
    

num = [-0.127838238013738, -0.122122430298337, -0.207240989159078, -0.741109041690890,  1.329553577868309]
den = [ 1.000000000000000, -0.445897866413142, -0.101209607292324, -0.047938888781208, -0.037189007185997]
def myabshilbert(x):
    return np.sqrt(scipy.signal.lfilter(num, den, x)[4:]**2 + x[:-4]**2)

def getHilb(sig):
    hor = np.zeros( shape=(sig.size//nchan - 4))
    hf1 = np.zeros( shape=(sig.size//nchan - 4))
    hf2 = np.zeros( shape=(sig.size//nchan - 4))
    for i in range(nchan):
        hor += myabshilbert(sig[i::nchan])


    kern_size = int(medfiltsize*freq)
    if (kern_size % 2) == 0:
        kern_size += 1

    #hf1 = scipy.signal.medfilt(hor, kernel_size=kern_size) + 0.1*hor
    hf1 = gmean(hor, kernel_size=31)
    n = 20001
    a = scipy.signal.firwin(n, [20, 1000], pass_zero=False, window='hanning', nyq=freq/2)

    hf2[:] = np.convolve(hf1, a, mode='same')
    hf2 = hf1

    return hor, hf1, hf2



sig = np.zeros(winSize*nchan)
for i in range(nchan):
    sig[i::nchan] = A[i+(loc-winSize//2)*nchan:i+(loc+winSize//2)*nchan:nchan].copy()

hor,hf1,hf2 = getHilb(sig)

plt.plot(np.linspace(0,1,hor.size),hor, 'C0.-', alpha=0.3)
plt.plot(np.linspace(0,1,hor.size),hf1, 'g.-', alpha=0.3)
plt.plot(np.linspace(0,1,hor.size),hf2, 'r.-', alpha=0.3)

plt.plot( (0,1), (hmin, hmin) , 'k-')
#plt.plot(sig, 'C2.-')

#plt.xlim( (0.50, 0.513) )

plt.show()
