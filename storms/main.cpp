#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <assert.h>
#include <math.h>

#include <QFile>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "common/sigcfg.h"
#include "common/signalfile.h"
#include "common/excludedintervals.h"
#include "common/compilerspecific.h"

struct ExcludeAllChannels : ExcludedInterval
{
    ExcludeAllChannels(qint64 start_, qint64 end_) {
        start = start_;
        end = end_;
        for(int i = 0; i < NumChannels; i++)
            chExcluded[i] = true;
    }
};

static void stormDetected(SignalFile &sigfile, float minlevel, int afterglue,
                          qint64 &regionStart, qint64 &regionEnd)
{
    SignalBuffer buffer(8*EODSamples);
    float *squareSum = buffer.ch(0);
    qint64 curPos = regionStart - buffer.bytes();
    int glueAvailable = afterglue;

    while(true) {
        if(UNLIKELY(curPos <= 0))
            curPos = 0;
        sigfile.seek(curPos);

        sigfile.readFilteredCh(buffer);
        buffer.diff();
        buffer.sumSquares(squareSum);

        for(int i = buffer.spc() - 1; i >= 0; i--) {
            if(squareSum[i] >= minlevel) {
                glueAvailable = afterglue;
                regionStart = curPos + i*BytesPerSample;
            }
            else if(--glueAvailable < 0) {
                curPos = -1;
                break;
            }
        }

        if(UNLIKELY(curPos <= 0))
            break;
        curPos -= buffer.bytes();
    }

    curPos = regionEnd;
    glueAvailable = afterglue;

    while(LIKELY(!sigfile.atEnd())) {
        sigfile.seek(curPos);

        sigfile.readFilteredCh(buffer);
        buffer.diff();
        buffer.sumSquares(squareSum);

        for(int i = 0; i < buffer.spc(); i++) {
            if(squareSum[i] >= minlevel) {
                glueAvailable = afterglue;
                regionEnd = curPos + i*BytesPerSample;
            }
            else if(--glueAvailable < 0) {
                curPos = -1;
                break;
            }
        }

        if(UNLIKELY(curPos <= 0))
            break;
        curPos += buffer.bytes();
    }

    sigfile.seek(regionEnd + BytesPerSample);
}

static void stormDetector(SignalFile &sigfile, QFile &outfile,
                          float minlevel, int glue, int stormsize, int afterglue)
{
    ExcludedIntervalList list;
    SignalBuffer buffer(8*EODSamples);
    float *squareSum = buffer.ch(0);

    int regionSize = 0;
    qint64 regionStart = 0;
    int glueAvailable = glue;

    while(LIKELY(!sigfile.atEnd())) {
        const qint64 bufStart = sigfile.pos();
        sigfile.readFilteredCh(buffer);
        buffer.diff();
        buffer.sumSquares(squareSum);
        for(int i = 0; i < buffer.spc(); i++) {
            if(squareSum[i] >= minlevel) {
                if(regionSize++ == 0)
                    regionStart =  bufStart + i*BytesPerSample;
                glueAvailable = glue;
                if(regionSize >= stormsize) {
                    qint64 regionEnd = regionStart;
                    stormDetected(sigfile, minlevel, afterglue, regionStart, regionEnd);
                    list.append(ExcludeAllChannels(regionStart, regionEnd));
                    break;
                }
            }
            else if(regionSize && (--glueAvailable < 0)) {
                regionSize = 0;
            }
        }
    }

    list.writeFile(outfile);
}

static int usage(const char *progname)
{
    fprintf(stderr, "%s [options] input.I32 storm.intervals\n",
            progname);
    fprintf(stderr, "options:\n"
            "  -n|--numtaps=n     Number of taps (lowpass filter)\n"
            "  -c|--cutoff=c      Cutoff frequency (lowpass filter)\n"
            "  -l|--minlevel=l    Minimum level to consider as valid signal\n"
            "  -g|--glue=g        Maximum number of samples between regions to glue\n"
            "  -s|--stormsize=s   Number of contiguous signal samples to consider as storm\n"
            "  -a|--afterglue=a   After-detection number of samples between regions to glue\n");
    return 1;
}

int main(int argc, char **argv)
{
    commonInit();

    int numtaps = defaultLowpassNumTaps;
    float cutoff = defaultLowPassCutoff;
    float minlevel = defaultMinLevel;
    int glue = defaultStormGlue;
    int stormsize = defaultStormSize;
    int afterglue = defaultStormAfterGlue;

    while(1) {
        int option_index = 0;
        static struct option long_options[] = {
            { "numtaps",     required_argument, 0, 'n' },
            { "cutoff",      required_argument, 0, 'c' },
            { "minlevel",    required_argument, 0, 'l' },
            { "glue",        required_argument, 0, 'g' },
            { "stormsize",   required_argument, 0, 's' },
            { "afterglue",   required_argument, 0, 'a' },
            { 0, 0, 0, 0 }
        };

        int c = getopt_long(argc, argv, "n:c:l:g:s:a:",
                            long_options, &option_index);
        if(c == -1)
            break;

        switch(c) {
        case 'n':
            numtaps = QString(optarg).toInt();
            break;
        case 'c':
            cutoff = QString(optarg).toFloat();
            break;
        case 'l':
            minlevel = QString(optarg).toFloat();
            break;
        case 'g':
            glue = QString(optarg).toInt();
            break;
        case 's':
            stormsize = QString(optarg).toInt();
            break;
        case 'a':
            afterglue = QString(optarg).toInt();
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

    stormDetector(sigfile, outfile, minlevel, glue, stormsize, afterglue);

    sigfile.close();
    outfile.close();
    return 0;
}
