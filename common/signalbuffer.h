#ifndef SIGNALBUFFER_H
#define SIGNALBUFFER_H

#include "sigcfg.h"

class SignalBuffer
{
public:
    explicit SignalBuffer(int samplesPerCh);
    ~SignalBuffer();
    int spc() const { return samplesPerChannel; }
    int bytes() const { return samplesPerChannel*BytesPerSample; }
    float *ch(int c) const { return samples[c]; }
    void diff();
    void sumSquares(float *out);
private:
    int samplesPerChannel;
    float **samples;
};

#endif // SIGNALBUFFER_H
