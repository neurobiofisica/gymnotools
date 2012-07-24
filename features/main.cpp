#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <limits>

#include "common/featureutil.h"
#include "common/commoninit.h"
#include "common/sigcfg.h"
#include "common/windowfile.h"
#include "common/compilerspecific.h"

static float  buf  [NumFeatures] ALIGN(16);
static double mean [NumFeatures] ALIGN(16);
static double stdev[NumFeatures] ALIGN(16);
static float minval[NumFeatures] ALIGN(16);
static float maxval[NumFeatures] ALIGN(16);

/**
 * Computes mean, stdev, minval and maxval of all features
 * over all infiles.
 * @returns the number of features
 */
static qint32 computeInfo(QList<WindowFile*> &infiles)
{
    assert(infiles.length() > 0);
    WindowFile * const firstFile = infiles.first();

    assert(firstFile->nextEvent());
    const qint32 samples = firstFile->getEventSamples();
    assert(samples <= NumFeatures);

    for(int i = 0; i < samples; i++) {
        mean  [i] = 0.;
        stdev [i] = 0.;
        minval[i] = +std::numeric_limits<float>::infinity();
        maxval[i] = -std::numeric_limits<float>::infinity();
    }

    double n = 0.;

    // Compute <x> in mean and <x^2> in std.
    // Only later std will contain the standard deviation.
    foreach(WindowFile * const infile, infiles) {
        while(infile->nextChannel()) {
            assert(infile->getEventSamples() == samples);
            infile->read((char*)buf, samples*sizeof(float));
            for(int i = 0; i < samples; i++) {
                const float s = buf[i];
                if(s < minval[i])
                    minval[i] = s;
                if(s > maxval[i])
                    maxval[i] = s;
                mean[i]  += s;
                stdev[i] += s*s;
            }
            n += 1.;
        }
    }

    // Finish the means and compute standard deviations
    const double eps = std::numeric_limits<float>::epsilon();
    for(int i = 0; i < samples; i++) {
        mean[i] /= n;
        stdev[i] = sqrt(stdev[i]/n - mean[i]*mean[i]);
        if(stdev[i] < eps)
            stdev[i] = eps;
    }

    return samples;
}

static void cmd_compute(WindowFile &infile, WindowFile &outfile)
{
    static float origSignal[EODSamples] ALIGN(16);
    static float featureData[NumFeatures] ALIGN(16);
    static FeatureProcessor worker(origSignal, featureData);

    while(infile.nextEvent()) {
        const qint64 off = infile.getEventOffset();
        const qint32 channels = infile.getEventChannels();

        assert(infile.getEventSamples() == EODSamples);
        outfile.writeEvent(off, NumFeatures, channels);

        for(int ch = 0; ch < channels; ch++) {
            infile.nextChannel();
            infile.read((char*)origSignal, EODSamples*sizeof(float));
            worker.process();
            outfile.writeChannel(infile.getChannelId(), featureData);
        }
    }
}

static void cmd_rescale_prepare(QFile &scalefile, QList<WindowFile*> &infiles)
{
    qint32 samples = computeInfo(infiles);

    // Restrict minval and maxval to remove outliers (values
    // outside a 4-sigma range) and sanitize the values
    const float eps = std::numeric_limits<float>::epsilon();
    for(int i = 0; i < samples; i++) {
        const float minallowed = mean[i] - 4.*stdev[i];
        const float maxallowed = mean[i] + 4.*stdev[i];
        if(minval[i] < minallowed)
            minval[i] = minallowed;
        if(maxval[i] > maxallowed)
            maxval[i] = maxallowed;

        if(isinf(minval[i]) || (minval[i] < 0.))
            minval[i] = 0.;
        if(isinf(maxval[i]) || (maxval[i] <= minval[i]))
            maxval[i] = minval[i] + eps;
    }

    scalefile.write((char*)minval, samples*sizeof(float));
    scalefile.write((char*)maxval, samples*sizeof(float));
}

static void cmd_rescale_apply(QFile &scalefile, QList<WindowFile*> &outfiles)
{
    const qint32 samples = readScaleFile(scalefile, minval, maxval);
    assert(samples <= NumFeatures);

    foreach(WindowFile * const outfile, outfiles) {
        while(outfile->nextChannel()) {
            assert(outfile->getEventSamples() == samples);

            qint64 pos = outfile->pos();
            outfile->read((char*)buf, samples*sizeof(float));

            rescaleFeatureWin(buf, minval, maxval, samples);

            outfile->seek(pos);
            outfile->write((char*)buf, samples*sizeof(float));
        }
    }
}

static int usage(const char *progname)
{
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "%s compute infile.spikes outfile.features\n"
            "  Compute FFT and DT-CWPT features from a spike file.\n", progname);
    fprintf(stderr, "%s rescale prepare outfile.scale infiles.features\n"
            "  Prepare rescaling factors that when applied to the infiles\n"
            "  would cause all features (besides 4-sigma outliers) to lie\n"
            "  in the range [-1,1].\n", progname);
    fprintf(stderr, "%s rescale apply infile.scale outfiles.features\n"
            "  Apply the rescaling factors to the outfiles.\n", progname);
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
            fprintf(stderr, "can't open spike file '%s' for reading.\n", argv[2]);
            return 1;
        }
        WindowFile outfile(argv[3]);
        if(!outfile.open(QIODevice::WriteOnly)) {
            fprintf(stderr, "can't open feature file '%s' for writing.\n", argv[3]);
            return 1;
        }
        cmd_compute(infile, outfile);
        outfile.close();
        infile.close();
    }
    else if(!strcmp(argv[1], "rescale")) {
        if(argc < 5)
            return usage(argv[0]);
        QFile scalefile(argv[3]);
        if(!strcmp(argv[2], "prepare")) {
            if(!scalefile.open(QIODevice::WriteOnly)) {
                fprintf(stderr, "can't open scale file '%s' for writing.\n", argv[3]);
                return 1;
            }
            QList<WindowFile*> infiles;
            for(int i = 4; i < argc; i++) {
                WindowFile *infile = new WindowFile(argv[i]);
                if(!infile->open(QIODevice::ReadOnly)) {
                    fprintf(stderr, "can't open feature file '%s' for reading.\n", argv[i]);
                    return 1;
                }
                infiles.append(infile);
            }
            cmd_rescale_prepare(scalefile, infiles);
            foreach(WindowFile * const infile, infiles) {
                infile->close();
            }
            scalefile.close();
        }
        else if(!strcmp(argv[2], "apply")) {
            if(!scalefile.open(QIODevice::ReadOnly)) {
                fprintf(stderr, "can't open scale file '%s' for reading.\n", argv[3]);
                return 1;
            }
            QList<WindowFile*> outfiles;
            for(int i = 4; i < argc; i++) {
                WindowFile *outfile = new WindowFile(argv[i]);
                if(!outfile->open(QIODevice::ReadWrite)) {
                    fprintf(stderr, "can't open feature file '%s' for reading and writing.\n", argv[i]);
                    return 1;
                }
                outfiles.append(outfile);
                cmd_rescale_apply(scalefile, outfiles);
                foreach(WindowFile * const outfile, outfiles) {
                    outfile->close();
                }
                scalefile.close();
            }
        }
        else return usage(argv[0]);
    }
    else return usage(argv[0]);

    return 0;
}
