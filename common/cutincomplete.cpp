#include "sigcfg.h"
#include "cutincomplete.h"

qint64 cutIncompleteAtStartOrEnd(SignalFile &file, float minlevel, bool atEnd)
{
    if(atEnd) {
        qint64 curPos = file.size() - EODSamples*BytesPerSample;
        // assert the position is aligned to the beginning of a sample
        curPos -= curPos % BytesPerSample;
        file.seek(curPos);
    }
    else {
        file.seek(0);
    }
    return cutIncompleteSpikes(file, minlevel, atEnd ? -1 : 1);
}

qint64 cutIncompleteSpikes(SignalFile &file, float minlevel, int direction)
{
    SignalBuffer buf(EODSamples);
    qint64 curPos = file.pos();
    int first_i = 0;

    if(direction == -1) {
        first_i = buf.spc() - 2;
    }

    const int desiredSilentSamples = EODSamples / 2;
    int silentSamples = 0;
    float *squareSum = buf.ch(0);

    while(file.seek(curPos)) {
        file.readFilteredCh(buf);
        buf.diff();
        buf.sumSquares(squareSum);
        for(int i = first_i; i < buf.spc() - 1 && i >= 0; i += direction) {
            if(squareSum[i] >= minlevel) {
                silentSamples = 0;
            }
            else {
                if(++silentSamples >= desiredSilentSamples)
                    return curPos + (i - direction*(desiredSilentSamples - 1)) * BytesPerSample;
            }
        }
        curPos += direction * buf.bytes();
    }

    return file.pos();
}
