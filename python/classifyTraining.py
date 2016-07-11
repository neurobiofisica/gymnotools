from __future__ import division
import sys
import svm
import windowfile

print('load model')
model = svm.libsvm.svm_load_model('/ssd/15o04000_15o04001_h.svmmodel')
print('load A')
A = windowfile.readwins(open('/ssd/15o04000_h.features'))
print('load B')
B = windowfile.readwins(open('/ssd/15o04001_h.features'))

probs = (svm.c_double*2)(0,0)

print('-')
counter = 0
tam = A.shape[0]
for i in xrange(tam):
    if i % 10000 == 0:
        sys.stdout.write('\rA:\t%d\t%d\t%f\t%d\t%f'%(i, tam, i / tam, counter, counter/(i+1)))
        sys.stdout.flush()
    x0, max_idx = svm.gen_svm_nodearray(B[i].tolist())
    c = svm.libsvm.svm_predict_probability(model, x0, probs)
    if c == 1:
        counter += 1
        #print('%f\t%f\t%f'%(c, probs[0], probs[1]))

print('\n\n')
print('A:\t%f'%(counter / tam))

print('-')
counter = 0
tam = B.shape[0]
for i in xrange(tam):
    if i % 10000 == 0:
        sys.stdout.write('\rB:\t%d\t%d\t%f\t%d\t%f'%(i, tam, i / tam, counter, counter/(i+1)))
        sys.stdout.flush()
    x0, max_idx = svm.gen_svm_nodearray(B[i].tolist())
    c = svm.libsvm.svm_predict_probability(model, x0, probs)
    if c == 1:
        counter += 1
        #print('%f\t%f\t%f'%(c, probs[0], probs[1]))

print('\n\n')
print('B:\t%f'%(counter / tam))
