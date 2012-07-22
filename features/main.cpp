#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <fftw3.h>

#include "common/commoninit.h"
#include "common/sigcfg.h"
#include "common/windowfile.h"
#include "common/static_log2.h"
#include "common/wfilts.h"
#include "common/compiler_specific.h"
#include "dtcwpt/dtcwpt.h"

static const int EODSamples_log2 = static_log2<EODSamples>::value;

static int usage(const char *progname)
{
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "%s compute infile.spikes outfile.features\n"
            "  Compute FFT and DT-CWPT features from a spike file.\n", progname);
    fprintf(stderr, "%s rescale file.features\n"
            "  Rescale a feature file so that each feature lies\n"
            "  in the range [-1,1].\n", progname);
    return 1;
}

void cmd_compute(WindowFile &infile, WindowFile &outfile)
{
    float buf[EODSamples];
    while(infile.nextEvent()) {
        const qint64 off = infile.getEventOffset();
        const qint32 channels = infile.getEventChannels();
        assert(infile.getEventSamples() == EODSamples);
        outfile.writeEvent(off, EODSamples, channels);
        for(int ch = 0; ch < channels; ch++) {
            infile.nextChannel();
            infile.read((char*)buf, EODSamples*sizeof(float));
            outfile.writeChannel(infile.getChannelId(), buf);
        }
    }
}

int main(int argc, char **argv)
{
    commonInit();

    if(argc < 3)
        return usage(argv[0]);

    if(!strcmp(argv[1], "compute")) {
        if(argc < 4)
            return usage(argv[0]);
        WindowFile infile(argv[2]);
        if(!infile.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open '%s' for reading.\n", argv[2]);
            return 1;
        }
        WindowFile outfile(argv[3]);
        if(!outfile.open(QIODevice::WriteOnly)) {
            fprintf(stderr, "can't open '%s' for writing.\n", argv[3]);
            return 1;
        }
        cmd_compute(infile, outfile);
        outfile.close();
        infile.close();
    }
    else if(!strcmp(argv[1], "rescale")) {

    }
    else return usage(argv[0]);

    return 0;
}
