#include <assert.h>
#include "compilerspecific.h"
#include "signalfile.h"
#include "sigutil.h"

SignalFile::~SignalFile()
{
    if(filter != NULL)
        delete [] filter;
}

void SignalFile::readCh(SignalBuffer &buf)
{
    const int readBufLen = buf.spc() * NumChannels;
    internalBuffer.reserve(readBufLen);
    float *readBuf = internalBuffer.buf();
    memset(readBuf, 0, readBufLen*sizeof(float));
    read((char*)readBuf, readBufLen*sizeof(float));
    int pos = 0;
    for(int i = 0; i < buf.spc(); i++) {
        for(int ch = 0; ch < NumChannels; ch++) {
            buf.ch(ch)[i] = readBuf[pos++];
        }
    }
}

void SignalFile::setFilter(int numtaps, float cutoff)
{
    numtaps = numtaps | 1;  // always use an odd number of taps
    if(numtaps != filterLen) {
        if(filter != NULL)
            delete [] filter;
        filter = new float[numtaps];
        filterLen = numtaps;
    }
    lowpassFIR(filter, numtaps, cutoff);
}

void SignalFile::readFilteredCh(SignalBuffer &buf)
{
    assert(filterLen > 0);
    const int additionalSamples = filterLen - 1;
    const int readBufLen = (buf.spc() + additionalSamples) * NumChannels;
    internalBuffer.reserve(readBufLen);
    float *readBuf = internalBuffer.buf();

    const int idealPadding = filterLen / 2;
    const qint64 curPos = this->pos();

    // adjust padding
    int actualPadding;
    qint64 pos;
    if(UNLIKELY(curPos < idealPadding*BytesPerSample)) {
        pos = 0;
        actualPadding = curPos/BytesPerSample;
    }
    else {
        pos = curPos - idealPadding*BytesPerSample;
        actualPadding = idealPadding;
    }

    // read data
    seek(pos);
    const int startInReadBuf = (idealPadding - actualPadding)*NumChannels;
    const int bytesToRead = (readBufLen - startInReadBuf)*sizeof(float);
    memset(readBuf, 0, readBufLen*sizeof(float));
    read((char*)&readBuf[startInReadBuf], bytesToRead);

    // compute the filtered data
    for(int ch = 0; ch < NumChannels; ch++) {
        for(int i = 0; i < buf.spc(); i++) {
            float outSample = 0.;
            for(int j = 0; j < filterLen; j++) {
                const float inSample = readBuf[(i+j)*NumChannels + ch];
                outSample += filter[j]*inSample;
            }
            buf.ch(ch)[i] = outSample;
        }
    }

    // rewind the file to just before the padding
    if(LIKELY(!atEnd()))
        seek(this->pos() - idealPadding*BytesPerSample);
}
