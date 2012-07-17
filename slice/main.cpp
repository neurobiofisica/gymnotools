#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "common/commoninit.h"
#include "common/sigcfg.h"
#include "common/windowfile.h"

#define DSFMT_MEXP 19937
#include "dsfmt/dSFMT.h"

static int query_range(WindowFile &infile)
{
    qint64 off;

    infile.nextEvent();
    off = infile.getEventOffset();
    puts(QString("first event:\n"
                   "  bytes:   %1\n"
                   "  samples: %2\n"
                   "  seconds: %3\n")
         .arg(off)
         .arg(off / BytesPerSample)
         .arg((off / BytesPerSample)/(double)SamplingRate, 0, 'f', 6)
         .toUtf8().data());

    while(infile.nextEvent());
    off = infile.getEventOffset();
    puts(QString("last event:\n"
                   "  bytes:   %1\n"
                   "  samples: %2\n"
                   "  seconds: %3\n")
         .arg(off)
         .arg(off / BytesPerSample)
         .arg((off / BytesPerSample)/(double)SamplingRate, 0, 'f', 6)
         .toUtf8().data());

    return 0;
}

static int usage(const char *progname)
{
    fprintf(stderr, "%s query-range infile\n"
            "  Outputs to stdout the range (in samples, bytes and seconds)\n"
            "  contained in infile.\n", progname);
    fprintf(stderr, "%s range infile start-end samples|bytes|seconds outfile\n"
            "  Slices infile from start to end (samples, bytes or seconds),\n"
            "  producing an outfile containing only that range.\n", progname);
    fprintf(stderr, "%s random infile [prob_1 outfile_1 [prob_2 outfile_2 [...]]\n"
            "  Slices infile randomly, outputing channels to outfile_i with\n"
            "  probability prob_i. Output files are guaranteed to be disjoint.\n",
            progname);
    return 1;
}

int main(int argc, char **argv) {
    commonInit();

    if(argc < 2)
        return usage(argv[0]);

    if(!strcmp(argv[1], "query-range")) {
        if(argc != 3)
            return usage(argv[0]);
        WindowFile *infile = new WindowFile(argv[2]);
        if(!infile->open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open file '%s'.\n", argv[2]);
            return 1;
        }
        query_range(*infile);
    }
    else if(!strcmp(argv[1], "range")) {
        if(argc != 6)
            return usage(argv[0]);
    }
    else if(!strcmp(argv[1], "random")) {
        if(argc < 3 || (argc % 2 != 1))
            return usage(argv[0]);
    }
    else return usage(argv[0]);

    return 0;
}
