#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <assert.h>
#include <math.h>
#include <db.h>
#include <limits>

#include <QString>
#include <QStringList>
#include <QFile>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "common/sigcfg.h"
#include "common/windowfile.h"

static int usage(const char *progname)
{
    fprintf(stderr, "%s iterate [options] recog.db in.spikes in.singlefish\n", progname);
    fprintf(stderr, "options:\n"
            "  -z|--saturation=a,b Low and high saturation levels\n"
            "  -d|--direction=d    Scan direction (positive or negative)\n\n");

    fprintf(stderr, "%s waveform [options] recog.db outA.spikes outB.spikes\n", progname);
    fprintf(stderr, "options:\n"
            "  -z|--saturation=a,b Low and high saturation levels to filter out\n"
            "  -a|--onlyabove=a    Only output spikes above this amplitude\n"
            "  -f|--fillsamples=f  Number of samples used to compute filling amplitude\n\n");

    fprintf(stderr, "%s export [options] recog.db out.txt\n", progname);
    fprintf(stderr, "options:\n"
            "  -i|--isiwindow=i    Misdetection window around twice and half the last ISI\n"
            "  -d|--distfactor=d   Maximum distance factor to fix ISI misdetection\n\n");

    return 1;
}

int main(int argc, char **argv)
{
    commonInit();
    if(argc < 3)
        return usage(argv[0]);

    if(!strcmp(argv[1], "iterate")) {

    }
    else if(!strcmp(argv[1], "waveform")) {

    }
    else if(!strcmp(argv[1], "export")) {

    }
    else return usage(argv[0]);

    return 0;
}
