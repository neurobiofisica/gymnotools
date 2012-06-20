#include "signalbuffer.h"

SignalBuffer::SignalBuffer(int samplesPerCh)
{
    samplesPerChannel = samplesPerCh;
    float *buffer = new float[NumChannels*samplesPerCh];
    samples = new float*[NumChannels];
    for(int i = 0, j = 0; i < NumChannels; i++, j += samplesPerCh) {
        samples[i] = &buffer[j];
    }
}

SignalBuffer::~SignalBuffer()
{
    delete [] samples[0];
    delete [] samples;
}

void SignalBuffer::diff()
{
    for(int ch = 0; ch < NumChannels; ch++) {
        float *chBuf = samples[ch];
        for(int i = 0; i < samplesPerChannel - 1; i++) {
            chBuf[i] = chBuf[i+1]-chBuf[i];
        }
        chBuf[samplesPerChannel - 1] = 0.f;
    }
}

void SignalBuffer::sumSquares(float *out)
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
