#ifndef SIGUTIL_H
#define SIGUTIL_H

#include <math.h>
#include "common/compiler_specific.h"

/**
 * Constructs a hamming window
 * @param win pointer to a vector which will hold the window
 * @param len length of the vector
 */
static AINLINE void hamming(float *win, int len) {
    for(int i = 0; i < len; i++)
        win[i] = 0.54 - 0.46 * cos(2.*M_PI*i/(len - 1.));
}

/**
 * Constructs a lowpass FIR filter with a hamming window
 * @param filt pointer to a vector which will hold the filter
 * @param numtaps length of the vector
 * @param cutoff fraction of the maximum frequency on which to cut-off
 */
void lowpassFIR(float *filt, int numtaps, float cutoff);

/**
 * Finds the maximum element of a vector in absolute value
 * @param sig vector
 * @param len length of the vector
 * @returns the maximum absolute value
 */
static AINLINE float maxAbsFloat(float *sig, int len) {
    float max = fabsf(sig[0]);
    for(int i = 1; i < len; i++) {
        const float sample = fabsf(sig[i]);
        if(sample > max)
            max = sample;
    }
    return max;
}

#endif // SIGUTIL_H
