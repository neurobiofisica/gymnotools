#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>

#include <QStringList>
#include <QRegExp>
#include <QtAlgorithms>
#include <QtDebug>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "common/sigcfg.h"
#include "common/signalfile.h"

struct ExcludedInterval
{
    qint64 start, end;
    bool chExcluded[NumChannels];

    bool operator<(const struct ExcludedInterval &other) const
    {
        return start < other.start;
    }
};

struct ExcludedIntervalList: QList<ExcludedInterval>
{
    void parseFile(QFile &file)
    {
        QRegExp rxLine("(\\d+)\\s*-\\s*(\\d+)\\s*:\\s*([0-9, ]+)\n?");
        QRegExp rxNum("(\\d+)");
        char line[1024];
        int lineno = 1;
        while(file.readLine(line, sizeof(line)) != -1) {
            // parse line using regex
            if(!rxLine.exactMatch(line)) {
                fprintf(stderr, "ExcludedIntervals: line %d: "
                        "malformed line\n", lineno++);
                continue;
            }
            // store start and end
            ExcludedInterval interval;
            interval.start = rxLine.cap(1).toLong() * BytesPerSample;
            interval.end   = rxLine.cap(2).toLong() * BytesPerSample;
            // sanity check [start, end]
            if(interval.end <= interval.start) {
                fprintf(stderr, "ExcludedIntervals: line %d: "
                        "interval ends before it starts\n",
                        lineno++);
                continue;
            }
            // initialize chExcluded
            for(int ch = 0; ch < NumChannels; ch++) {
                interval.chExcluded[ch] = false;
            }
            // parse the channel list
            foreach(const QString &str, rxLine.cap(3).split(",")) {
                if(rxNum.indexIn(str) == -1) {
                    fprintf(stderr, "ExcludedIntervals: line %d: "
                            "malformed channel\n", lineno++);
                    continue;
                }
                int ch = rxNum.cap(1).toInt();
                if(ch < 0 || ch >= NumChannels) {
                    fprintf(stderr, "ExcludedIntervals: line %d: "
                            "channel %d outside range\n",
                            lineno++, ch);
                    continue;
                }
                interval.chExcluded[ch] = true;
            }
            // append the interval
            this->append(interval);
            // increase line number
            lineno++;
        }
        // assert the container is sorted
        qSort(this->begin(), this->end());
    }
};

static int usage(const char *progname)
{
    fprintf(stderr, "%s [options] input.I32 output.spikes\n",
            progname);
    fprintf(stderr, "options:\n"
            "  -f|--fixedwin       Fixed window (use for single-fish data files)\n"
            "  -n|--numtaps=n      Number of taps (lowpass filter)\n"
            "  -c|--cutoff=c       Cutoff frequency (lowpass filter)\n"
            "  -d|--detection=d    Threshold for detecting a spike\n"
            "  -l|--minlevel=l     Minimum level to stop detection\n"
            "  -r|--minratio=r     Ratio of the maximum level to stop detection\n"
            "  -s|--stopsamples=s  Samples below level to stop detection\n"
            "  -e|--exclude=file   File containing intervals/channels to exclude\n");
    return 1;
}

int main(int argc, char **argv)
{
    commonInit();

    bool fixedwin = false;
    int numtaps = defaultLowpassNumTaps;
    float cutoff = defaultLowPassCutoff;
    float detection = defaultDetectionThreshold;
    float minlevel = defaultMinLevel;
    float minratio = defaultMinRatio;
    int stopsamples = defaultStopSamples;
    ExcludedIntervalList intervals;

    while(1) {
        int option_index = 0;
        static struct option long_options[] = {
            { "fixedwin",    no_argument,       0, 'f' },
            { "numtaps",     required_argument, 0, 'n' },
            { "cutoff",      required_argument, 0, 'c' },
            { "detection",   required_argument, 0, 'd' },
            { "minlevel",    required_argument, 0, 'l' },
            { "minratio",    required_argument, 0, 'r' },
            { "stopsamples", required_argument, 0, 's' },
            { "exclude",     required_argument, 0, 'e' },
            { 0, 0, 0, 0 }
        };

        int c = getopt_long(argc, argv, "fn:c:d:l:r:s:e:",
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
                intervals.parseFile(file);
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


    return 0;
}
