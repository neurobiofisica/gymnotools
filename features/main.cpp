#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <assert.h>
#include <math.h>
#include <limits>

#include <QPair>
#include <QList>
#include <QStringList>
#include <QTextStream>
#include <QtAlgorithms>

#include "common/featureutil.h"
#include "common/commoninit.h"
#include "common/sigcfg.h"
#include "common/windowfile.h"
#include "common/compilerspecific.h"

// determines the range outside which values are considered outliers
static const float nonOutlierSigma = 4.;

static float  buf  [NumFeatures] ALIGN(16);
static double mean [NumFeatures] ALIGN(16);
static double stdev[NumFeatures] ALIGN(16);
static float minval[NumFeatures] ALIGN(16);
static float maxval[NumFeatures] ALIGN(16);

/**
 * Computes mean, stdev, minval and maxval of all features
 * over all infiles. Store those in global vectors.
 * @returns the number of features
 */
static qint32 computeInfo(QList<WindowFile*> &infiles)
{
    assert(infiles.length() > 0);
    WindowFile * const firstFile = infiles.first();

    bool hasEvents = firstFile->nextEvent();
    assert(hasEvents);
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

    // Sanitize the minimum and maximum values
    for(int i = 0; i < samples; i++) {
        if(isinf(minval[i]))
            minval[i] = maxval[i];
        if(isinf(maxval[i]) || (maxval[i] <= minval[i]))
            maxval[i] = minval[i] + eps;
    }

    return samples;
}

struct Histogram
{
    float *intervals;
    double **hist;
    double n;
    int maxBars;
    int samples;

    /**
     * Compute a histogram for each of the samples contained in a window file.
     * The minimum and maximum values for each sample must be precomputed.
     * @param infile the window file
     * @param numbars desired number of histogram bars
     * @param minval minimum values for each sample
     * @param maxval maximum values for each sample
     * @param veclen length of the vectors (number of samples)
     * @param stdev if provided, numbars is applied to a 1-sigma range
     */
    Histogram(WindowFile &infile, int numbars,
              const float *minval, const float *maxval, int veclen,
              const double *stdev = NULL)
    {
        samples = veclen;
        intervals = new float[veclen];
        if(stdev == NULL) {
            for(int i = 0; i < veclen; i++)
                intervals[i] = (maxval[i] - minval[i]) / numbars;
        }
        else {
            for(int i = 0; i < veclen; i++)
                intervals[i] = 2.*stdev[i] / numbars;
        }

        maxBars = 0;
        for(int i = 0; i < veclen; i++) {
            const int bars = (int)((maxval[i] - minval[i]) / intervals[i]) + 1;
            if(bars > maxBars)
                maxBars = bars;
        }

        hist = new double*[veclen];
        hist[0] = new double[veclen * maxBars];
        for(int i = 1; i < veclen; i++) {
            hist[i] = &hist[i-1][maxBars];
        }

        for(int i = 0; i < veclen; i++)
            for(int j = 0; j < maxBars; j++)
                hist[i][j] = 0.;

        n = 0.;
        float *buf = new float[veclen];
        while(infile.nextChannel()) {
            assert(infile.getEventSamples() == veclen);
            infile.read((char*)buf, veclen*sizeof(float));
            for(int i = 0; i < veclen; i++) {
                const int bar = (buf[i] - minval[i]) / intervals[i];
                hist[i][bar] += 1.;
            }
            n += 1.;
        }
        delete[] buf;

        for(int i = 0; i < veclen; i++)
            for(int j = 0; j < maxBars; j++)
                hist[i][j] /= n;
    }    
    ~Histogram()
    {
        delete[] intervals;
        delete[] hist[0];
        delete[] hist;
    }

    /**
     * Computes the overlapping area below two histograms
     * @param other another histogram, which must have the same 'samples' and 'maxBars'
     * @param out output vector, which must have length equal to 'samples'
     */
    void overlap(const Histogram &other, double *out)
    {
        assert(other.samples == samples);
        assert(other.maxBars == maxBars);
        for(int i = 0; i < samples; i++) {
            out[i] = 0.;
            for(int j = 0; j < maxBars; j++) {
                out[i] += qMin(hist[i][j], other.hist[i][j]);
            }
        }
    }
};

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

    // Restrict minval and maxval to remove outliers
    for(int i = 0; i < samples; i++) {
        const float minallowed = mean[i] - nonOutlierSigma*stdev[i];
        const float maxallowed = mean[i] + nonOutlierSigma*stdev[i];
        if(minval[i] < minallowed)
            minval[i] = minallowed;
        if(maxval[i] > maxallowed)
            maxval[i] = maxallowed;
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

static void filter_prepare_best(bool *featureIncl, int n, double *overlap, int samples, bool waveletOnly=false)
{
    typedef QPair<double,int> DoubleIntPair;
    QList<DoubleIntPair> overlapList;
    for(int i = 0; i < samples; i++)
        overlapList.append(DoubleIntPair(overlap[i], i));
    qSort(overlapList);
    foreach(const DoubleIntPair &pair, overlapList) {
        const int idx = pair.second;
        if(waveletOnly && idx < NumFFTFeatures)
            continue;
        if(!featureIncl[idx]) {
            featureIncl[idx] = true;
            if(--n == 0)
                break;
        }
    }
}

static double bestbasis_cb(void *arg, int level, unsigned int off, unsigned int n)
{
    double *dtcwptOverlap = (double *)arg;
    int totalOffset = level * EODSamples + off;
    double metric = 0.;
    for(unsigned int i = 0; i < n; i++) {
        const double x = dtcwptOverlap[totalOffset + i];
        metric -= x * log2(x);
    }
    return metric;
}

static void filter_prepare_bestbasis(bool *featureIncl, double *overlap)
{
    unsigned int nps;
    cwpt_stop_point *ps = bestbasis_find(bestbasis_cb, &overlap[NumFFTFeatures],
                                         BESTBASIS_MIN, EODSamples, &nps);
    for(unsigned int i = 0; i < nps; i++) {
        const cwpt_stop_point *p = &ps[i];
        const unsigned int lev = EODSamples_log2 - p->level;
        const unsigned int off = (p->node << lev) + (p->level * EODSamples);
        const unsigned int len = 1 << lev;
        for(unsigned int i = 0; i < len; i++) {
            featureIncl[NumFFTFeatures + off + i] = true;
        }
    }
    free(ps);
}

enum FiltPrepOpId {
    FILT_PREP_ADD,
    FILT_PREP_BESTBASIS,
    FILT_PREP_BEST,
    FILT_PREP_BESTW
};
struct FiltPrepOp {
    FiltPrepOpId opid;
    int arg1, arg2;
};

static void cmd_filter_prepare(QList<FiltPrepOp> &oplist, int histBars, bool histStd,
                               QFile &outfile, WindowFile &fileA, WindowFile &fileB)
{
    QList<WindowFile*> fileList;
    fileList.append(&fileA);
    fileList.append(&fileB);

    qint32 samples = computeInfo(fileList);
    assert(samples <= NumFeatures);
    if(samples != NumFeatures)
        fprintf(stderr, "warning: input feature files are already filtered\n");

    fileA.rewind();
    fileB.rewind();

    Histogram histogramA(fileA, histBars, minval, maxval, samples, histStd ? stdev : NULL);
    Histogram histogramB(fileB, histBars, minval, maxval, samples, histStd ? stdev : NULL);

    double overlap[NumFeatures];
    histogramA.overlap(histogramB, overlap);

    bool featureIncl[NumFeatures];
    for(int i = 0; i < NumFeatures; i++)
        featureIncl[i] = false;

    foreach(const FiltPrepOp &op, oplist) {
        switch(op.opid) {
        case FILT_PREP_ADD:
            for(int i = op.arg1; i <= op.arg2; i++) {
                assert(i >= 0); assert(i < NumFeatures);
                featureIncl[i] = true;
            }
            break;
        case FILT_PREP_BESTBASIS:
            assert(samples == NumFeatures);
            filter_prepare_bestbasis(featureIncl, overlap);
            break;
        case FILT_PREP_BEST:
	case FILT_PREP_BESTW:
            filter_prepare_best(featureIncl, op.arg1, overlap, samples, op.opid == FILT_PREP_BESTW);
            break;
        }
    }

    QTextStream stream(&outfile);
    for(int i = 0; i < samples; i++) {
        if(featureIncl[i]) {
            stream << i << '\n';
        }
    }
}

static void cmd_filter_apply(QFile &filterfile, WindowFile &infile, WindowFile &outfile)
{
    static float origFeatures[NumFeatures] ALIGN(16);
    static float filtFeatures[NumFeatures] ALIGN(16);
    FeatureFilter worker(filterfile);

    bool hasEvents = infile.nextEvent();
    assert(hasEvents);
    const qint32 samples = infile.getEventSamples();
    assert(worker.maxIndex() < samples);

    do {
        const qint64 off = infile.getEventOffset();
        const qint32 channels = infile.getEventChannels();

        assert(infile.getEventSamples() == samples);
        outfile.writeEvent(off, worker.length(), channels);

        for(int ch = 0; ch < channels; ch++) {
            infile.nextChannel();
            infile.read((char*)origFeatures, samples*sizeof(float));
            worker.filter(origFeatures, filtFeatures);
            outfile.writeChannel(infile.getChannelId(), filtFeatures);
        }
    } while(infile.nextEvent());
}

static int usage(const char *progname)
{
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "%s compute infile.spikes outfile.features\n"
            "  Compute FFT and DT-CWPT features from a spike file.\n", progname);
    fprintf(stderr, "%s rescale prepare outfile.scale infiles.features\n"
            "  Prepare rescaling factors that when applied to the infiles would cause\n"
            "  features (besides outliers outside a %.0f-sigma range) to lie in the\n"
            "  [-1,1] range.\n", progname, nonOutlierSigma);
    fprintf(stderr, "%s rescale apply infile.scale outfiles.features\n"
            "  Apply the rescaling factors to the outfiles.\n", progname);
    fprintf(stderr, "%s filter prepare [options] out.filter A.features B.features\n"
            "  Prepare a feature filter by reading features of distinct experimental\n"
            "  subjects A and B, producing out.filter.\n"
            "  Available options:\n"
            "    --add=a,b      add features in the interval [a,b]\n"
            "    --fft          add all FFT features (same as --add=0,%d)\n"
            "    --bestbasis    add DT-CWPT bestbasis features\n"
            "    --best=n       add n best (less histogram overlap) features\n"
            "    --bestw=n      add n best DT-CWPT (less histogram overlap) features\n"
            "    --hist-bars=n  use n bars for the histogram\n"
            "    --hist-std=n   use n bars around an one-sigma range for the histogram\n",
            progname, NumFFTFeatures-1);
    fprintf(stderr, "%s filter apply infile.filter infile.features outfile.features\n"
            "  Apply the feature filter to infile, producing outfile.\n", progname);
    return 1;
}

int main(int argc, char **argv)
{
    const char *progname = argv[0];
    assert(EODSamples % 4 == 0);   // required for alignment
    commonInit();

    if(argc < 2)
        return usage(progname);

    if(!strcmp(argv[1], "compute")) {
        if(argc != 4)
            return usage(progname);
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
            return usage(progname);
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
        else return usage(progname);
    }
    else if(!strcmp(argv[1], "filter")) {
        if(argc < 3)
            return usage(progname);
        if(!strcmp(argv[2], "prepare")) {
            QList<FiltPrepOp> oplist;
            int histBars = 20;
            bool histStd = true;

            argc -= 2;
            argv = &argv[2];

            while(1) {
                int option_index = 0;
                static struct option long_options[] = {
                    { "add",       required_argument, 0, 1 },
                    { "fft",       no_argument,       0, 2 },
                    { "bestbasis", no_argument,       0, 3 },
                    { "best",      required_argument, 0, 4 },
                    { "bestw",     required_argument, 0, 5 },
                    { "hist-bars", required_argument, 0, 6 },
                    { "hist-std",  required_argument, 0, 7 },
                    { 0, 0, 0, 0 }
                };

                int c = getopt_long(argc, argv, "", long_options, &option_index);
                if(c == -1)
                    break;

                FiltPrepOp op;
                bool ok1 = false, ok2 = false;
                QStringList sl;

                switch(c) {
                case 1:
                    op.opid = FILT_PREP_ADD;
                    sl = QString(optarg).split(",");
                    if(sl.count() != 2) {
                        fprintf(stderr, "--add argument must be a list of two numbers\n");
                        return 1;
                    }
                    op.arg1 = sl.at(0).toInt(&ok1);
                    op.arg2 = sl.at(1).toInt(&ok2);
                    if(!ok1 || !ok2) {
                        fprintf(stderr, "--add arguments must be numbers\n");
                        return 1;
                    }
                    if(op.arg1 < 0 || op.arg1 >= NumFeatures) {
                        fprintf(stderr, "--add: %d is outside the range [0,%d)\n", op.arg1, NumFeatures);
                        return 1;
                    }
                    if(op.arg2 < 0 || op.arg2 >= NumFeatures) {
                        fprintf(stderr, "--add: %d is outside the range [0,%d)\n", op.arg2, NumFeatures);
                        return 1;
                    }
                    if(op.arg2 < op.arg1) {
                        fprintf(stderr, "--add: invalid interval from %d to %d\n", op.arg1, op.arg2);
                        return 1;
                    }
                    oplist.append(op);
                    break;
                case 2:
                    op.opid = FILT_PREP_ADD;
                    op.arg1 = 0;
                    op.arg2 = NumFFTFeatures - 1;
                    oplist.append(op);
                    break;
                case 3:
                    op.opid = FILT_PREP_BESTBASIS;
                    oplist.append(op);
                    break;
                case 4:
                case 5:
                    op.opid = (c == 4) ? FILT_PREP_BEST : FILT_PREP_BESTW;
                    op.arg1 = QString(optarg).toInt(&ok1);
                    if(!ok1) {
                        fprintf(stderr, "invalid number '%s' passed as --best/--bestw argument\n", optarg);
                        return 1;
                    }
                    if(op.arg1 < 0 || op.arg1 > NumFeatures) {
                        fprintf(stderr, "--best/--bestw: %d is outside the range [0,%d]\n", op.arg1, NumFeatures);
                        return 1;
                    }
                    oplist.append(op);
                    break;
                case 6:
                case 7:
                    histStd = (c == 7);
                    histBars = QString(optarg).toInt(&ok1);
                    if(!ok1) {
                        fprintf(stderr, "invalid number '%s'\n", optarg);
                        return 1;
                    }
                    break;
                default:
                    return usage(progname);
                }
            }

            if(argc - optind != 3)
                return usage(progname);


            QFile outfile(argv[optind]);
            if(!outfile.open(QIODevice::WriteOnly)) {
                fprintf(stderr, "can't open filter file '%s' for writing\n", argv[optind+2]);
                return 1;
            }

            WindowFile fileA(argv[optind+1]), fileB(argv[optind+2]);
            if(!fileA.open(QIODevice::ReadOnly)) {
                fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind]);
                return 1;
            }
            if(!fileB.open(QIODevice::ReadOnly)) {
                fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind+1]);
                return 1;
            }

            cmd_filter_prepare(oplist, histBars, histStd, outfile, fileA, fileB);

            outfile.close();
            fileA.close();
            fileB.close();
        }
        else if(!strcmp(argv[2], "apply")) {
            if(argc != 6)
                return usage(progname);
            QFile filterfile(argv[3]);
            if(!filterfile.open(QIODevice::ReadOnly)) {
                fprintf(stderr, "can't open filter file '%s' for reading.\n", argv[3]);
                return 1;
            }
            WindowFile infile(argv[4]);
            if(!infile.open(QIODevice::ReadOnly)) {
                fprintf(stderr, "can't open feature file '%s' for reading.\n", argv[4]);
                return 1;
            }
            WindowFile outfile(argv[5]);
            if(!outfile.open(QIODevice::WriteOnly)) {
                fprintf(stderr, "can't open feature file '%s' for writing.\n", argv[5]);
                return 1;
            }
            cmd_filter_apply(filterfile, infile, outfile);
            filterfile.close();
            infile.close();
            outfile.close();
        }
        else return usage(progname);
    }
    else return usage(progname);

    return 0;
}
