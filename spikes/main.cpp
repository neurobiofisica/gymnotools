#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <limits>

#include <QStringList>
#include <QtDebug>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "common/sigcfg.h"
#include "common/signalfile.h"
#include "common/excludedintervals.h"
#include "common/cutincomplete.h"

class ExcludingCapableSignalBuffer : public SignalBuffer
{
public:
    explicit ExcludingCapableSignalBuffer(int samplesPerCh)
        :SignalBuffer(samplesPerCh)
    {
    }

    void sumSquares(float *out)
    {
        SignalBuffer::sumSquares(out);
    }

    void sumSquares(float *out, const bool *chExcluded)
    {
        for(int i = 0; i < samplesPerChannel; i++) {
            float outSample = 0.;
            for(int ch = 0; ch < NumChannels; ch++) {
                if(!chExcluded[ch]) {
                    const float inSample = samples[ch][i];
                    outSample += inSample*inSample;
                }
            }
            out[i] = outSample;
        }
    }
};

static int spikeDiscriminator(SignalFile &sigfile, QFile &outfile, bool fixedwin,
                               float detection, float onlyabove, float minlevel,
                               float minratio, int stopsamples,
                               float saturationLow, float saturationHigh,
                               ExcludedIntervalList &excluded)
{
    ExcludingCapableSignalBuffer buffer(16*EODSamples);
    float *squareSum = buffer.ch(0);   // we will always overwrite ch(0) with
                                       // the sum of squares

    const qint64 fileStart = cutIncompleteAtStartOrEnd(sigfile, minlevel, false);
    const qint64 fileEnd   = cutIncompleteAtStartOrEnd(sigfile, minlevel, true);

    sigfile.seek(fileStart);

    // abort if intervals overlap with fileStart or fileEnd
    if(excluded.count() > 0) {
        if(excluded.at(0).end < fileStart) {
            fprintf(stderr, "error: first interval overlaps with fileStart=%lld\n", fileStart);
            return 1;
        }
        if(excluded.at(excluded.count() - 1).start >= fileEnd) {
            fprintf(stderr, "error: last interval overlaps with fileEnd=%lld\n", fileEnd);
            return 1;
        }
    }

    ExcludedIntervalList::ConstIterator excl;
    for(excl = excluded.constBegin(); excl != excluded.constEnd(); ++excl) {
        // process data until the start of the next interval
        qint64 stopAt = (*excl).start;
        while(sigfile.pos() < stopAt) {
            const qint64 bufStart = sigfile.pos();
            sigfile.readFilteredCh(buffer);
            buffer.diff();
            buffer.sumSquares(squareSum);
            int numSamples = buffer.spc() - 1; // one less because of diff()
            // if the current buffer contains part of a interval
            if(sigfile.pos() > stopAt) {
                // some samples shouldn't be checked
                numSamples -= (sigfile.pos() - stopAt)/BytesPerSample;
            }
            for(int i = 0; i < numSamples; i++) {
                if(squareSum[i] >= detection) {
                    sigfile.seek(bufStart + i*BytesPerSample);
                    // process the spike at bufStart + i*BytesPerSample
                }
            }
        }

        // process data until the end of the current interval

        sigfile.seek(stopAt);
        stopAt = (*excl).end;

        int numExcluded = 0;
        for(int i = 0; i < NumChannels; i++) {
            numExcluded += (*excl).chExcluded[i];
        }

        while(sigfile.pos() <= stopAt) {
            const qint64 bufStart = sigfile.pos();
            sigfile.readFilteredCh(buffer);
            buffer.diff();
            buffer.sumSquares(squareSum, (*excl).chExcluded);
            int numSamples = buffer.spc() - 1; // one less because of diff()
            // if the current buffer contains part of a interval
            if(sigfile.pos() > stopAt) {
                // some samples shouldn't be checked
                numSamples -= (sigfile.pos() - stopAt)/BytesPerSample;
            }
            for(int i = 0; i < numSamples; i++) {
                if(squareSum[i] >= detection) {
                    sigfile.seek(bufStart + i*BytesPerSample);
                    // process the spike at bufStart + i*BytesPerSample
                }
            }
        }

        sigfile.seek(stopAt + BytesPerSample);
    }

    // no excluded intervals remaining, process until the end of the file
    while(sigfile.pos() <= fileEnd) {
        const qint64 bufStart = sigfile.pos();
        sigfile.readFilteredCh(buffer);
        buffer.diff();
        buffer.sumSquares(squareSum);
        for(int i = 0; i < buffer.spc() - 1; i++) {
            if(squareSum[i] >= detection) {
                sigfile.seek(bufStart + i*BytesPerSample);
                // process the spike at bufStart + i*BytesPerSample
            }
        }
    }

    return 0;
}

static int usage(const char *progname)
{
    fprintf(stderr, "%s [options] input.I32 output.spikes\n",
            progname);
    fprintf(stderr, "options:\n"
            "  -f|--fixedwin       Fixed window (use for single-fish data files)\n"
            "  -n|--numtaps=n      Number of taps (lowpass filter)\n"
            "  -c|--cutoff=c       Cutoff frequency (lowpass filter)\n"
            "  -d|--detection=d    Threshold for detecting a spike\n"
            "  -a|--onlyabove=a    Only output spikes above this amplitude\n"
            "  -l|--minlevel=l     Minimum level to stop detection\n"
            "  -r|--minratio=r     Ratio of the maximum level to stop detection\n"
            "  -s|--stopsamples=s  Samples below level to stop detection\n"
            "  -e|--exclude=file   File containing intervals/channels to exclude\n"
            "  -z|--saturation=a,b Low and high saturation levels to filter out\n");
    return 1;
}

int main(int argc, char **argv)
{
    commonInit();

    bool fixedwin = false;
    int numtaps = defaultLowpassNumTaps;
    float cutoff = defaultLowPassCutoff;
    float detection = defaultDetectionThreshold;
    float onlyabove = 0.;
    float minlevel = defaultMinLevel;
    float minratio = defaultMinRatio;
    int stopsamples = defaultStopSamples;
    float saturationLow = -std::numeric_limits<float>::infinity();
    float saturationHigh = std::numeric_limits<float>::infinity();
    ExcludedIntervalList excluded;

    while(1) {
        int option_index = 0;
        static struct option long_options[] = {
            { "fixedwin",    no_argument,       0, 'f' },
            { "numtaps",     required_argument, 0, 'n' },
            { "cutoff",      required_argument, 0, 'c' },
            { "detection",   required_argument, 0, 'd' },
            { "onlyabove",   required_argument, 0, 'a' },
            { "minlevel",    required_argument, 0, 'l' },
            { "minratio",    required_argument, 0, 'r' },
            { "stopsamples", required_argument, 0, 's' },
            { "exclude",     required_argument, 0, 'e' },
            { "saturation",  required_argument, 0, 'z' },
            { 0, 0, 0, 0 }
        };

        int c = getopt_long(argc, argv, "fn:c:d:l:r:s:e:z:",
                            long_options, &option_index);
        if(c == -1)
            break;

        switch(c) {
        case 'f':
            fixedwin = true;
            break;
        case 'n':
            numtaps = QString(optarg).toInt();
            break;
        case 'c':
            cutoff = QString(optarg).toFloat();
            break;
        case 'd':
            detection = QString(optarg).toFloat();
            break;
        case 'a':
            if(!strcmp(optarg, "def")) {
                onlyabove = defaultOnlyAbove;
            }
            else {
                onlyabove = QString(optarg).toFloat();
            }
            break;
        case 'l':
            minlevel = QString(optarg).toFloat();
            break;
        case 'r':
            minratio = QString(optarg).toFloat();
            break;
        case 's':
            stopsamples = QString(optarg).toInt();
            break;
        case 'e':
            {
                QFile file(optarg);
                if(!file.open(QIODevice::ReadOnly)) {
                    fprintf(stderr, "Can't open exclude file (%s).\n", optarg);
                    return 1;
                }
                excluded.parseFile(file);
            }
            break;
        case 'z':
            if(!strcmp(optarg, "def")) {
                saturationLow = defaultSaturationLow;
                saturationHigh = defaultSaturationHigh;
            }
            else {
                QStringList sl = QString(optarg).split(",");
                if(sl.count() != 2) {
                    fprintf(stderr, "--saturation argument must be 'def' or"
                            " a list of two numbers\n");
                    return 1;
                }
                saturationLow = sl.at(0).toFloat();
                saturationHigh = sl.at(1).toFloat();
            }
            break;
        default:
            return usage(argv[0]);
        }
    }

    if(argc - optind != 2)
        return usage(argv[0]);

    const char *inFilename = argv[optind];
    SignalFile sigfile(inFilename);
    sigfile.setFilter(numtaps, cutoff);

    if(!sigfile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "Can't open input file (%s).\n", inFilename);
        return 1;
    }

    const char *outFilename = argv[optind+1];
    QFile outfile(outFilename);

    if(!outfile.open(QIODevice::WriteOnly)) {
        fprintf(stderr, "Can't open output file (%s).\n", outFilename);
        return 1;
    }

    return spikeDiscriminator(sigfile, outfile, fixedwin, detection,
                              onlyabove, minlevel, minratio, stopsamples,
                              saturationLow, saturationHigh, excluded);
}

