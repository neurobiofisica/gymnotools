#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>

#include "common/commoninit.h"
#include "paramchooser/defaultparams.h"

static int usage(const char *progname) {
    fprintf(stderr, "%s [options] input.I32 output.spikes\n",
            progname);
    fprintf(stderr, "options:\n"
            "  -f|--fixedwin       Fixed window (use for single-fish data files)\n"
            "  -n|--numtaps=n      Number of taps (lowpass filter)\n"
            "  -c|--cutoff=c       Cutoff frequency (lowpass filter)\n"
            "  -d|--detection=d    Threshold for detecting a spike\n"
            "  -l|--minlevel=l     Minimum level to stop detection\n"
            "  -r|--minratio=r     Ratio of the maximum amplitude to stop detection\n"
            "  -s|--stopsamples=s  Samples below level to stop detection\n");
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
            { 0, 0, 0, 0 }
        };

        int c = getopt_long(argc, argv, "fn:c:d:l:r:s:",
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
        default:
            return usage(argv[0]);
        }
    }

    if(argc - optind != 2)
        usage(argv[0]);


    return 0;
}
