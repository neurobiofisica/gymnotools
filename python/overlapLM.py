from __future__ import division

from sklearn import ensemble
import sklearn
import windowfile
import numpy as np
import matplotlib.pyplot as plt
import sys
import pickle

print('load')
A = windowfile.readwins(open(sys.argv[1]))
B = windowfile.readwins(open(sys.argv[2]))

tamA = A.shape[0]
tamB = B.shape[0]

trainingSize = 10000

singleSet = np.zeros((trainingSize, 256))
overlapSet = np.zeros((trainingSize, 256))

print('generate set')
for i in xrange(trainingSize):
    # single
    sA = int(np.random.rand() * tamA)
    sB = int(np.random.rand() * tamB)
    if np.random.rand() > 0.5: # from A
        singleSet[i, :] = A[sA]
    else:
        singleSet[i, :] = B[sA]

    # overlap
    ov = np.zeros(256)
    if np.random.rand() > 0.5: # A fixed
        ov += A[sA]
        left = (np.random.rand() > 0.5)
        offset = int(np.random.rand() * 128)
        if left:
            ov[:(256 - offset)] += B[sB][offset:]
        else:
            ov[offset:] += B[sB][:(256-offset)]
    else:
        ov += B[sB]
        left = (np.random.rand() > 0.5)
        offset = int(np.random.rand() * 128)
        if left:
            ov[:(256 - offset)] += A[sA][offset:]
        else:
            ov[offset:] += A[sA][:(256-offset)]
    overlapSet[i] = ov


print('train model')
Features = np.concatenate( (singleSet, overlapSet), axis=0)
Classes = np.zeros( (2*trainingSize) )
Classes[trainingSize:] = 1 # 1 to overlap

Nshuffles = 10
nfolds = 5
scores = np.zeros( (Nshuffles, nfolds) )
idxs = np.arange(0, 2*trainingSize, 1)
'''for shf in xrange(Nshuffles):
    print(shf)
    np.random.shuffle(idxs)

    clf_rf = ensemble.RandomForestClassifier(n_estimators=200)

    scores[shf,:] = sklearn.cross_validation.cross_val_score(clf_rf, Features[idxs], Classes[idxs], cv=nfolds)

print('')
print(scores)
print(scores.mean())'''

clf_rf = ensemble.RandomForestClassifier(n_estimators=200).fit(Features,Classes)
pickle.dump( clf_rf, open("RandomForestOverlapModel.pickle", 'wb'), protocol=2)
