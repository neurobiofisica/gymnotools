#include "sigutil.h"

void lowpassFIR(float *filt, int numtaps, float cutoff) {
    if(numtaps == 1) {
        filt[0] = 1.;
        return;
    }
    float sum = 0.;
    float m2 = (numtaps-1.)/2.;
    hamming(filt, numtaps);
    for(int i = 0; i < numtaps; i++) {
        float arg = M_PI*(i-m2);
        if(fabs(arg) > 1.e-5)
            filt[i] *= sin(cutoff*arg)/arg;
        else
            filt[i] *= cutoff;
        sum += filt[i];
    }
    for(int i = 0; i < numtaps; i++)
        filt[i] /= sum;
}
