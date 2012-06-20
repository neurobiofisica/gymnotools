#ifndef SIGUTIL_H
#define SIGUTIL_H

#include <math.h>

static inline void hamming(float *win, int len) {
    for(int i = 0; i < len; i++)
        win[i] = 0.54 - 0.46 * cos(2.*M_PI*i/(len - 1.));
}

void lowpassFIR(float *filt, int numtaps, float cutoff);

static inline float maxAbsFloat(float *sig, int len) {
    float max = fabsf(sig[0]);
    for(int i = 1; i < len; i++) {
        const float sample = fabsf(sig[i]);
        if(sample > max)
            max = sample;
    }
    return max;
}

#endif // SIGUTIL_H
