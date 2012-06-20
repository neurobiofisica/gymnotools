#ifndef SIGNALBUFFER_H
#define SIGNALBUFFER_H

#include "sigcfg.h"

class SignalBuffer
{
public:
    explicit SignalBuffer(int samplesPerCh);
    ~SignalBuffer();

    /**
     * Samples per channel
     * @returns number of samples
     */
    int spc() const { return samplesPerChannel; }

    /**
     * Bytes occupied by the entire buffer (all channels)
     * @returns number of bytes
     */
    int bytes() const { return samplesPerChannel*BytesPerSample; }

    /**
     * Contents of a channel
     * @returns pointer to a vector containing channel data
     */
    float *ch(int c) const { return samples[c]; }

    /**
     * Differentiate the signal of all channels
     */
    void diff()
    {
        for(int ch = 0; ch < NumChannels; ch++) {
            float *chBuf = samples[ch];
            for(int i = 0; i < samplesPerChannel - 1; i++) {
                chBuf[i] = chBuf[i+1]-chBuf[i];
            }
            chBuf[samplesPerChannel - 1] = 0.f;
        }
    }

    /**
     * Sum squares of all channels
     * @param out pointer to the output vector (can be the same as one of the inputs)
     */
    void sumSquares(float *out)
    {
        for(int i = 0; i < samplesPerChannel; i++) {
            float outSample = 0.;
            for(int ch = 0; ch < NumChannels; ch++) {
                const float inSample = samples[ch][i];
                outSample += inSample*inSample;
            }
            out[i] = outSample;
        }
    }

private:
    int samplesPerChannel;
    float **samples;
};

#endif // SIGNALBUFFER_H
