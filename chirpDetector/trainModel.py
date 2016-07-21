import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from sklearn import svm, datasets, ensemble, tree
import sklearn

import pickle

import sys
if sys.version_info.major == 3:
    xrange = range


crossValidate = False
scoreVerbosity = False
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

            feat = np.concatenate(
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

# aux arrays

if crossValidate == True:
    # Number of shufflings
    Nshuffles = 10
    nfolds    = 5

    scores = np.zeros( (Nshuffles, nfolds) )
    idxs = np.arange(0, Ndata, 1)

    for shf in range(Nshuffles):

        # Shuffling
        np.random.shuffle(idxs)

        # Cross-validating
        clf_rf = ensemble.RandomForestClassifier(n_estimators=200)

        scores[shf,:] = sklearn.cross_validation.cross_val_score(clf_rf,
                                                                Features[idxs],
                                                                Classes[idxs],
                                                                cv=nfolds)

    # Printing average scores
    print(scores)
    print(scores.mean())

# Running random a forest
clf_rf = ensemble.RandomForestClassifier(n_estimators=200).fit(Features,Classes)
if scoreVerbosity == True:
    print ("RandomForest score: %4.3f" % clf_rf.score(Xtest,Ytest) )

pickle.dump( clf_rf, open("RandonForestChirpModel_abs__tmp.pickle", 'wb'), protocol=2)
