#ifndef FEATUREUTIL_H
#define FEATUREUTIL_H

#include <assert.h>
#include <QFile>
#include <QList>
#include <QTextStream>

#include <complex.h>
#ifndef complex
#define complex
#endif
#include <fftw3.h>

#include "sigcfg.h"
#include "sigutil.h"
#include "windowfile.h"
#include "static_log2.h"
#include "wfilts.h"
#include "compilerspecific.h"
#include "dtcwpt/dtcwpt.h"

static const int EODSamples_log2 = static_log2<EODSamples>::value;
static const int NumFFTFeatures = EODSamples/2;
static const int NumDTCWPTFeatures = EODSamples*(1 + EODSamples_log2);
static const int NumFeatures = NumFFTFeatures + NumDTCWPTFeatures;

class FeatureProcessor
{
private:
    fftwf_complex fftSignal[1 + NumFFTFeatures] ALIGN(16);
    float dtcwptOut1[NumDTCWPTFeatures] ALIGN(16);
    float dtcwptOut2[NumDTCWPTFeatures] ALIGN(16);

    fftwf_plan fftPlan;

    afloat * const origSignal;
    afloat * const featureData;

public:
    /**
     * Constructs a feature processor
     * @param orig pointer to an aligned vector used to pass original signal
     * @param features pointer to an aligned vector which will receive features
     */
    FeatureProcessor(afloat *orig, afloat *features)
        :origSignal(orig), featureData(features)
    {
        fftPlan = fftwf_plan_dft_r2c_1d(EODSamples, orig, fftSignal, 0);
    }

    /**
     * Processes a window of signal
     */
    void process()
    {
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
    }

    ~FeatureProcessor()
    {
        fftwf_destroy_plan(fftPlan);
    }
};

/**
 * Reads a feature scaling file
 * @param scalefile the file
 * @param minval receives the minimum values
 * @param maxval receives the maximum values
 * @returns number of features (samples)
 */
static AINLINE qint32 readScaleFile(QFile &scalefile, float *minval, float *maxval)
{
    const qint32 samples = scalefile.size() / sizeof(float) / 2;
    scalefile.read((char*)minval, samples*sizeof(float));
    scalefile.read((char*)maxval, samples*sizeof(float));
    return samples;
}

/**
 * Rescales a feature window
 * @param win the window to rescale
 * @param minval as read by readScaleFile
 * @param maxval as read by readScaleFile
 * @param samples number of features
 */
static AINLINE void rescaleFeatureWin(afloat *win, afloat *minval, afloat *maxval, qint32 samples) {
    for(int i = 0; i < samples; i++)
        win[i] = 2.*((win[i] - minval[i])/(maxval[i]-minval[i])) - 1.;
}

class FeatureFilter
{
private:
    int len;
    int sel[NumFeatures];
    int maxidx;
public:
    /**
     * Set selection list from the contents of a QList<int>
     * @param selected the list
     */
    void setSelected(const QList<int> &selected)
    {
        assert(selected.length() <= NumFeatures);
        len = selected.length();
        int i = 0;
        maxidx = 0;
        foreach(const int x, selected) {
            sel[i++] = x;
            if(x > maxidx)
                maxidx = x;
        }
    }
    /**
     * Set selection list from the contents of a QFile
     * @param filterFile the file
     */
    void readFromFile(QFile &filterFile)
    {
        QList<int> selected;
        QTextStream stream(&filterFile);
        while(true) {
            int x; stream >> x;
            if(stream.status() != QTextStream::Ok)
                break;
            selected.append(x);
        }
        setSelected(selected);
    }
    /**
     * Filter the in vector, producing the out vector
     * @param in the in aligned vector
     * @param out the out aligned vector
     */
    void filter(afloat *in, afloat *out)
    {
        for(int i = 0; i < len; i++) {
            out[i] = in[sel[i]];
        }
    }
    /**
     * Get the length of the loaded selection list
     */
    int length() const
    {
        return len;
    }
    /**
     * Get the maximum index selected by the loaded selection list
     */
    int maxIndex() const
    {
        return maxidx;
    }
    FeatureFilter() :len(0),maxidx(0) { }
    explicit FeatureFilter(const QList<int> &selected) { setSelected(selected); }
    explicit FeatureFilter(QFile &filterFile) { readFromFile(filterFile); }
};

#endif // FEATUREUTIL_H
