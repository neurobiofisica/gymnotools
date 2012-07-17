#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "common/commoninit.h"
#include "common/windowfile.h"

#define DSFMT_MEXP 19937
#include "dsfmt/dSFMT.h"

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
