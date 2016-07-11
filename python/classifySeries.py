from __future__ import division
import sys
import svm
import windowfile
import pickle
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sg

print('load model')
model = svm.libsvm.svm_load_model('/ssd/15o04000_15o04001_h.svmmodel')
print('load A')
A = windowfile.readwins(open('/ssd/15o03000_h.features'))
print('load sig')
sig = windowfile.readwinsEx(open('/ssd/15o03000_h.spikes'))
print('load randomForest')
clf = pickle.load( open("RandomForestOverlapModel.pickle", 'rb'))


state = 'single'
probs = (svm.c_double*2)(0,0)
pA = 1.
pB = 1.
maxamp = 0.
sigs_now = []
#H = np.zeros(256)

print('-')
counter = 0
tam = A.shape[0]
for i in xrange(tam):
    if i % 10000 == 0:
        sys.stdout.write('\rA:\t%d\t%d\t%f\t%d\t%f'%(i, tam, i / tam, counter, counter/(i+1)))
        sys.stdout.flush()
    x0, max_idx = svm.gen_svm_nodearray(A[i].tolist())
    c = svm.libsvm.svm_predict_probability(model, x0, probs)
    off, ch, sig_now = sig.next()
    M = abs(sig_now).max()
    pA *= probs[0] ** M
    pB *= probs[1] ** M
    maxamp += M
    sigs_now.append(sig_now)
    #H += np.abs(sg.hilbert(sig_now))
    if (i+1) % 11 == 0:
        pA = pA ** (1. / maxamp)
        pB = pB ** (1. / maxamp)

        fig = plt.figure(1,figsize=(16,16))
        timer = fig.canvas.new_timer(interval=2000)
        def close_event():
            plt.close()
        timer.add_callback(close_event)

        '''idx, = np.where(H > 0.2*H.max())
        t = idx.size
        if t > 60:
            state = 'overlap'
        else:
            state = 'single' '''
        overlapCounter = 0
        if clf.predict(sigs_now).sum() > 5:
            state = 'overlap'
        else:
            state = 'single'




        if pA > pB:
            if state == 'single':
                color = 'b'
            else:
                color = 'c'
        else:
            if state == 'single':
                color = 'r'
            else:
                color = 'm'
        for j in xrange(11):
            plt.plot(sigs_now[j], color=color)
        plt.title('%f - %f -- (%s)'%(pA, pB, state) )

        timer.start()
        plt.show()

        maxamp = 0.
        pA = 1.
        pB = 1.
        sigs_now = []
        #H.fill(0.)
    if c == 1:
        counter += 1
        #print('%f\t%f\t%f'%(c, probs[0], probs[1]))

print('\n\n')
print('A:\t%f'%(counter / tam))

