import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from sklearn import svm, datasets, ensemble, tree
import sklearn

import pickle

import sys
if sys.version_info.major == 3:
    xrange = range

WindowSize = 2000

def distort(x, baseline=0.2):
    return baseline + (1-baseline)/(1+x**2)

def getFeatures(listTimeSeries, WindowSize, walk=23, win=100):

    feat = np.zeros( (1, (WindowSize)) )

    for tseries in listTimeSeries:
        nwindows = int( tseries.shape[0]/WindowSize )

        for j in range( nwindows ):
            f = tseries[j*WindowSize:(j+1)*WindowSize]
            f = f*distort(f)

            #s = np.clip(tseries[j*WindowSize:(j+1)*WindowSize], -0.2, 0.2)
            #f = np.zeros(s.size-win)
            #for i in xrange(s.size-win):
                #f[i] = np.std(s[i:i+win])
            #f = np.abs(np.fft.fft(f))#[:int(f.size/2)]
            #f = f[:int(f.size/2)]
            #f2 = np.diff(np.diff(tseries))[j*WindowSize+walk:(j+1)*WindowSize+walk]
            #if f.size != f2.size:
            #    continue
            feat = np.concatenate(
                #(feat, [np.abs(np.fft.fft(tseries[j*WindowSize:(j+1)*WindowSize]))]), axis=0 )
                #(feat, [ tseries[j*WindowSize:(j+1)*WindowSize] ]), axis=0 )
                (feat, [f]), axis=0 )

    return feat


## Getting the time series

chirps = []

f = open("chirps.txt", "r")
for line in f:
    X = np.array( line.split("\n")[0].split(" ")[:-1], dtype=float)
    chirps.append(X)

nochirps = []

f = open("without_chirps.txt", "r")
for line in f:
    X = np.array( line.split("\n")[0].split(" ")[:-1], dtype=float)
    nochirps.append(X)


## Splitting in time windows

features_chirp   = getFeatures(chirps, WindowSize)
features_nochirp = getFeatures(nochirps, WindowSize)

nchir = features_chirp.shape[0]
nnoch = features_nochirp.shape[0]

print ("Data with chirp:    ", nchir)
print ("Data without chirp: ", nnoch)
print ("Prior with chirp: %4.3f" % ( float(nchir)/(nnoch+nchir) ) )



## Preparing for the ML algorithms

Ndata = nnoch + nchir

Features = np.concatenate( (features_chirp, features_nochirp), axis = 0 )

Classes  = np.zeros( (Ndata) )
Classes[:nchir] = 1

# Number of shufflings
Nshuffles = 10
nfolds    = 5

# aux arrays
scores = np.zeros( (Nshuffles, nfolds) )
idxs = np.arange(0, Ndata, 1)

for shf in range(Nshuffles):

    # Shuffling
    np.random.shuffle(idxs)

    # Cross-validating
    clf_rf = ensemble.RandomForestClassifier(n_estimators=200)

    #clf_rf = ensemble.AdaBoostClassifier(tree.DecisionTreeClassifier(max_depth=5),
    #                            algorithm = "SAMME",
    #                            n_estimators = 200 )

    scores[shf,:] = sklearn.cross_validation.cross_val_score(clf_rf,
                                                            Features[idxs],
                                                            Classes[idxs],
                                                            cv=nfolds)

# Printing average scores
print(scores)
print(scores.mean())

# Running random a forest
clf_rf = ensemble.RandomForestClassifier(n_estimators=200).fit(Features,Classes)
#print ("RandomForest score: %4.3f" % clf_rf.score(Xtest,Ytest) )

pickle.dump( clf_rf, open("RandonForestChirpModel_abs__tmp.pickle", 'wb'), protocol=2)

# Running a SVM with RBF kernel (not optimized!!)
'''maxscr = 0
best_values = None
for c in np.logspace(-5, 15, 21, base=2):
    for g in np.logspace(-15, 3, 19, base=2):
        clf_svm = svm.SVC( kernel='rbf', gamma=g, C=c ).fit(Xtrain,Ytrain)
        scr_now = clf_svm.score(Xtest,Ytest)
        if scr_now > maxscr:
            maxscr = scr_now
            best_values = (c, g)
        print('c=2**%f\tg=2**%f\tscr=%f\tbest_scr=%f'%(np.log2(c),np.log2(g),scr_now,maxscr))

print ("SVM score: %4.3f\tc=2**%f\tg=2**%f" % (maxscr, np.log2(best_values[0]), np.log2(best_values[1])))
#clf_svm = svm.SVC( kernel='rbf', gamma=.001, C=10000. ).fit(Xtrain,Ytrain)
#print ("SVM score: %4.3f" % clf_svm.score(Xtest,Ytest) )
'''

# Plot wrong evaluations
'''n=0
for i in range(len(Xtest)):
    if clf_rf.score([Xtest[i]],[Ytest[i]]) == 0:
        if Ytest[i] == 0:
            color='b'#nonchirp classified as chirp
        else:
            color='r' #chirp classified as nonchirp (never should happen!!)
        plt.plot(1*n + Xtest[i], color)
        n+=1
plt.show()'''
