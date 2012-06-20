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
