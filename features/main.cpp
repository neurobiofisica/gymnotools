#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <complex.h>
#include <fftw3.h>

#include "common/commoninit.h"
#include "common/sigcfg.h"
#include "common/sigutil.h"
#include "common/windowfile.h"
#include "common/static_log2.h"
#include "common/wfilts.h"
#include "common/compilerspecific.h"
#include "dtcwpt/dtcwpt.h"

static const int EODSamples_log2 = static_log2<EODSamples>::value;
static const int NumFFTFeatures = EODSamples/2;
static const int NumDTCWPTFeatures = EODSamples*(1 + EODSamples_log2);
static const int NumFeatures = NumFFTFeatures + NumDTCWPTFeatures;

static void cmd_compute(WindowFile &infile, WindowFile &outfile)
{
    static float origSignal[EODSamples] ALIGN(16);
    static fftwf_complex fftSignal[1 + NumFFTFeatures] ALIGN(16);
    static float dtcwptOut1[NumDTCWPTFeatures] ALIGN(16);
    static float dtcwptOut2[NumDTCWPTFeatures] ALIGN(16);
    static float featureData[NumFeatures] ALIGN(16);

    fftwf_plan fftPlan = fftwf_plan_dft_r2c_1d(EODSamples, origSignal, fftSignal, 0);

    while(infile.nextEvent()) {
        const qint64 off = infile.getEventOffset();
        const qint32 channels = infile.getEventChannels();

        assert(infile.getEventSamples() == EODSamples);
        outfile.writeEvent(off, NumFeatures, channels);

        for(int ch = 0; ch < channels; ch++) {
            infile.nextChannel();
            infile.read((char*)origSignal, EODSamples*sizeof(float));

            // Compute FFT of the signal
            fftwf_execute(fftPlan);

            // Take the absolute value of each FFT component
            // (discarding the DC component)
            for(int i = 0; i < NumFFTFeatures; i++)
                featureData[i] = cabsf(fftSignal[i+1]);

            // Compute DT-CWPT of the signal and put after the
            // FFT components in featureData
            cwpt_fulltree(&tree1_filt, origSignal, EODSamples, dtcwptOut1);
            cwpt_fulltree(&tree2_filt, origSignal, EODSamples, dtcwptOut2);
            dtcwpt_mix(dtcwptOut1, dtcwptOut2, NumDTCWPTFeatures, &featureData[NumFFTFeatures]);

            // Normalize featureData
            normalizeAlignedFloat(featureData, NumFFTFeatures);
            for(int i = NumFFTFeatures; i < NumFeatures; i += EODSamples)
                normalizeAlignedFloat(&featureData[i], EODSamples);

            outfile.writeChannel(infile.getChannelId(), featureData);
        }
    }

    fftwf_destroy_plan(fftPlan);
}

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

int main(int argc, char **argv)
{
    assert(EODSamples % 4 == 0);   // required for alignment
    commonInit();

    if(argc < 3)
        return usage(argv[0]);

    if(!strcmp(argv[1], "compute")) {
        if(argc != 4)
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
