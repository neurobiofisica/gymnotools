#include "sigcfg.h"
#include "cutincomplete.h"

qint64 cutIncompleteSpikes(SignalFile &file, bool atEnd, float minlevel) {
    SignalBuffer buf(EODSamples);
    qint64 curPos = 0;
    int first_i = 0;
    int direction = 1;

    if(atEnd) {
        direction = -1;
        first_i = buf.spc() - 2;
        curPos = file.size() - buf.bytes();
        // assert the position is aligned to the beginning of a sample
        curPos -= curPos % BytesPerSample;
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
