#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <assert.h>
#include <math.h>
#include <limits>

#include <QString>
#include <QStringList>
#include <QFile>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "common/sigcfg.h"
#include "common/windowfile.h"
#include "common/signalfile.h"
#include "common/compilerspecific.h"
#include "common/resizablebuffer.h"

static AINLINE void findSingleFish(SignalFile &sigfile, WindowFile &winfile, QFile &outfile,
                                   float onlyabove, float saturationLow, float saturationHigh,
                                   int minwins, float minprob, int maxdist, int maxsize)
{
    ResizableBuffer buf(maxsize);
    qint64 prevOff = std::numeric_limits<qint64>::min();

    while(winfile.nextEvent()) {
        const qint64 curOff = winfile.getEventOffset();
        const int eventSamples = winfile.getEventSamples();

        // Check if event is below maxsize
        if(eventSamples > maxsize)
            continue;

        // Calculate and check distance to next and previous events

        qint64 nextOff = std::numeric_limits<qint64>::max();
        if(winfile.nextEvent()) {
            nextOff = winfile.getEventOffset();
            winfile.prevEvent();
        }
        const int distPrev = (curOff - prevOff) / BytesPerSample;
        const int distNext = (nextOff - curOff) / BytesPerSample;
        prevOff = curOff;

        if(distPrev > maxdist && distNext > maxdist)
            continue;

        assert(winfile.getEventChannels() <= NumChannels);
        int numWinOk = 0;
        bool winOk[NumChannels];

        // Verify which channels can be used to feed the SVM

        for(int i = 0; i < winfile.getEventChannels(); i++) {
            winfile.nextChannel();
            const int ch = winfile.getChannelId();
            assert(ch < NumChannels);
            winOk[ch] = false;

            buf.reserve(eventSamples);
            winfile.read((char*)buf.buf(), eventSamples*sizeof(float));

            bool chOk = false;
            for(int i = 0; i < eventSamples; i++) {
                const float sample = buf.buf()[i];
                if(!chOk && fabsf(sample) >= onlyabove)
                    chOk = true;
                if(sample <= saturationLow || sample >= saturationHigh) {
                    chOk = false;
                    break;
                }
            }
            if(chOk) {
                winOk[ch] = true;
                numWinOk++;
            }
        }


    }
}

static int usage(const char *progname)
{
    fprintf(stderr, "%s [options] in.I32 in.spikes out.singlefish\n",
            progname);
    fprintf(stderr, "options:\n"
            "  -a|--onlyabove=a    Only analyze with SVM if above this amplitude\n"
            "  -z|--saturation=a,b Low and high saturation levels to filter out\n"
            "  -w|--minwins=w      Minimum windows needed to analyze with SVM\n"
            "  -p|--minprob=p      Minimum SVM probability to consider as single-fish\n"
            "  -d|--maxdist=d      Maximum distance to the next or previous spike\n"
            "  -s|--maxsize=s      Maximum size of a single-fish spike window\n");
    return 1;
}

int main(int argc, char **argv)
{
    commonInit();

    float onlyabove = defaultOnlyAbove;
    float saturationLow = defaultSaturationLow;
    float saturationHigh = defaultSaturationHigh;
    int minwins = defaultSingleMinWins;
    float minprob = defaultSingleMinProb;
    int maxdist = defaultSingleMaxDist;
    int maxsize = EODSamples;

    while(1) {
        int option_index = 0;
        static struct option long_options[] = {
            { "onlyabove",  required_argument, 0, 'a' },
            { "saturation", required_argument, 0, 'z' },
            { "minwins",    required_argument, 0, 'w' },
            { "minprob",    required_argument, 0, 'p' },
            { "maxdist",    required_argument, 0, 'd' },
            { "maxsize",    required_argument, 0, 's' },
            { 0, 0, 0, 0 }
        };

        int c = getopt_long(argc, argv, "a:z:w:p:d:s:",
                            long_options, &option_index);
        if(c == -1)
            break;

        switch(c) {
        case 'a':
            onlyabove = QString(optarg).toFloat();
            break;
        case 'z':
        {
            QStringList sl = QString(optarg).split(",");
            if(sl.count() != 2) {
                fprintf(stderr, "--saturation argument must be  a list of two numbers\n");
                return 1;
            }
            saturationLow = sl.at(0).toFloat();
            saturationHigh = sl.at(1).toFloat();
        }
        case 'w':
            minwins = QString(optarg).toInt();
            break;
        case 'p':
            minprob = QString(optarg).toFloat();
            break;
        case 'd':
            maxdist = QString(optarg).toInt();
            break;
        case 's':
            maxsize = QString(optarg).toInt();
            break;
        default:
            return usage(argv[0]);
        }
    }

    if(argc - optind != 3)
        return usage(argv[0]);

    SignalFile sigfile(argv[optind]);
    if(!sigfile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "Can't open input data file (%s).\n", argv[optind]);
        return 1;
    }

    WindowFile winfile(argv[optind+1]);
    if(!winfile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "Can't open input spike file (%s).\n", argv[optind+1]);
        return 1;
    }

    QFile outfile(argv[optind+2]);
    if(!outfile.open(QIODevice::WriteOnly)) {
        fprintf(stderr, "Can't open output file (%s).\n", argv[optind+2]);
        return 1;
    }

    findSingleFish(sigfile, winfile, outfile, onlyabove, saturationLow, saturationHigh,
                   minwins, minprob, maxdist, maxsize);

    sigfile.close();
    winfile.close();
    outfile.close();

    return 0;
}
