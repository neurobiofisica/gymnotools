#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <assert.h>
#include <math.h>
#include <limits>

#include <QString>
#include <QStringList>
#include <QFile>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "common/sigcfg.h"
#include "common/windowfile.h"
#include "common/signalfile.h"
#include "common/compilerspecific.h"
#include "common/resizablebuffer.h"
#include "common/featureutil.h"
#include "common/svmutil.h"
#include "svm/svm.h"

static AINLINE void findSingleFish(SignalFile &sigfile, WindowFile &winfile,
                                   afloat *minval, afloat *maxval,
                                   FeatureFilter &feafilter, svm_model *model, QFile &outfile, QFile &completeoutfile,
                                   float onlyabove, float saturationLow, float saturationHigh,
                                   int minwins, float minprob, int maxdist, int maxsize)
{
    ResizableBuffer winbuf(maxsize);
    SignalBuffer sigbuf(EODSamples);
    qint64 prevOff = std::numeric_limits<qint64>::min();
    int prevSamples = 0;

    bool prevWasSingle = false, prevWasA = false;
    qint64 prevOffBck;

    static float origSignal[EODSamples] ALIGN(16);
    static float featureData[NumFeatures] ALIGN(16);
    static float featureFilt[NumFeatures] ALIGN(16);
    static FeatureProcessor worker(origSignal, featureData);
    static SVMNodeList nodelist(feafilter.length());

    while(winfile.nextEvent()) {
        const qint64 curOff = winfile.getEventOffset();
        const int winSamples = winfile.getEventSamples();

        char cause = 's';

        // Check if event is below maxsize
        if(winSamples > maxsize) {
            prevWasSingle = false;
            prevSamples = winSamples;
            prevOff = curOff;

            cause = 'a';
        }

        // Calculate and check distance to next and previous events

        qint64 nextOff = std::numeric_limits<qint64>::max();
        if(winfile.nextEvent()) {
            nextOff = winfile.getEventOffset();
            winfile.prevEvent();
        }
        const int distPrev = (curOff - prevOff) / BytesPerSample;
        const int distNext = (nextOff - curOff) / BytesPerSample;
        const qint64 prevEndOff = prevOff + prevSamples * BytesPerSample;
        prevSamples = winSamples;
        prevOffBck = prevOff;
        prevOff = curOff;

        if(distPrev > maxdist && distNext > maxdist) {
            prevWasSingle = false;

            cause = 'm';
        }

        // Verify which channels can be used to feed the SVM

        assert(winfile.getEventChannels() <= NumChannels);
        int numWinOk = 0;
        bool winOk[NumChannels];
        double maxAmp[NumChannels];

        for(int ch = 0; ch < NumChannels; ch++)
            winOk[ch] = false;

        for(int i = 0; i < winfile.getEventChannels(); i++) {
            bool errorless = winfile.nextChannel();
            assert(errorless);
            const int ch = winfile.getChannelId();
            assert(ch < NumChannels);

            winbuf.reserve(winSamples);
            winfile.read((char*)winbuf.buf(), winSamples*sizeof(float));

            bool chOk = false;
            for(int j = 0; j < winSamples; j++) {
                const float sample = winbuf.buf()[j];
                if(!chOk && fabsf(sample) >= onlyabove)
                    chOk = true;
                if(sample <= saturationLow || sample >= saturationHigh) {
                    chOk = false;
                    break;
                }
                if (fabs(sample) > maxAmp[ch]) {
                    maxAmp[ch] = fabs(sample);
                }
            }
            if(chOk) {
                winOk[ch] = true;
                numWinOk++;
            }
        }

        // Check if there are sufficient windows to trust SVM
        if(numWinOk < minwins) {
            prevWasSingle = false;

            cause = 'i';
        }

        // Read centered EODSamples from the signal file
        sigfile.seek(curOff + ((winSamples - EODSamples) / 2) * BytesPerSample);
        // Check if sigbuf data overlaps with the next or the previous window
        const qint64 curEndOff = sigfile.pos() + winSamples * BytesPerSample;
        if((prevEndOff > sigfile.pos()) || (curEndOff > nextOff)) {
            prevWasSingle = false;

            cause = 'o';
        }
        sigfile.readCh(sigbuf);

        // Feed SVM and calculate joint probability

        double probA = 1., probB = 1.;
        //double probA = 0., probB = 0.;
        double TotalMaxAmp = 0;

        for(int ch = 0; ch < NumChannels; ch++) {
            if(!winOk[ch])
                continue;

            // Compute features
            float *chbuf = sigbuf.ch(ch);
            memcpy(origSignal, chbuf, sizeof(origSignal));
            worker.process();

            // Rescale features
            rescaleFeatureWin(featureData, minval, maxval, NumFeatures);

            // Filter features
            feafilter.filter(featureData, featureFilt);

            // Apply SVM
            double probEstim[2] = {0., 0.};
            nodelist.fill(featureFilt);
            svm_predict_probability(model, nodelist, probEstim); //////////////////
            // Independent channels
            //probA *= probEstim[0];
            //probB *= probEstim[1];

            // Aritmetic mean
            //probA += probEstim[0] * maxAmp[ch];
            //probB += probEstim[1] * maxAmp[ch];

            //TotalMaxAmp += maxAmp[ch];

            // Weighted geometric mean
            probA *= pow(probEstim[0], 1./maxAmp[ch]);
            probB *= pow(probEstim[1], 1./maxAmp[ch]);

            TotalMaxAmp += 1./maxAmp[ch];
        }

        // Try to make a geometric mean on the probability
        //probA = pow(probA, 1./numWinOk);
        //probB = pow(probB, 1./numWinOk);

        // Aritmetic mean
        //probA = probA / TotalMaxAmp;
        //probB = probB / TotalMaxAmp;

        // Weighted geometric mean
        probA = pow(probA, 1./TotalMaxAmp);
        probB = pow(probB, 1./TotalMaxAmp);


        // Check if joint probability is above minimum
        if(probA < minprob && probB < minprob) {
            prevWasSingle = false;

            cause = 'p';
        }

        // Everything OK, write event pair offsets to outfile
        if (cause == 's') {
            if(prevWasSingle) {

                // Write TS and probs on complete outfile
                if(prevWasA && (probB > probA)) {
                    completeoutfile.write(QString("s %1 %2 %3 %4\n")
                                            .arg(curOff)
                                            .arg(prevOffBck)
                                            .arg(probA)
                                            .arg(probB)
                                            .toAscii());

                    outfile.write(QString("%1 %2\n") //////////////////
                                  .arg(prevOffBck)
                                  .arg(curOff)
                                  .toAscii());
                    prevWasSingle = false;
                    continue;
                }
                else if(!prevWasA && (probA > probB)) {
                    completeoutfile.write(QString("s %1 %2 %3 %4\n")
                                            .arg(curOff)
                                            .arg(prevOffBck)
                                            .arg(probA)
                                            .arg(probB)
                                            .toAscii());

                    outfile.write(QString("%1 %2\n")
                                  .arg(curOff)
                                  .arg(prevOffBck)
                                  .toAscii());
                    prevWasSingle = false;
                    continue;
                }
                else {
                    completeoutfile.write(QString("w %1 %2 %3 %4\n")
                                            .arg(curOff)
                                            .arg(prevOffBck)
                                            .arg(probA)
                                            .arg(probB)
                                            .toAscii());
                }

            }
            else {
                // Write TS and probs on complete outfile
                completeoutfile.write(QString("c %1 %2 %3 %4\n")
                                        .arg(curOff)
                                        .arg(0)
                                        .arg(probA)
                                        .arg(probB)
                                        .toAscii());
            }

            prevWasA = (probA > probB);
            prevWasSingle = true;
        }
        else {
            completeoutfile.write(QString("%1 %2 %3 %4 %5\n")
                                  .arg(cause)
                                  .arg(curOff)
                                  .arg(0)
                                  .arg(probA)
                                  .arg(probB)
                                  .toAscii());
        }
    }
}

static int usage(const char *progname)
{
    fprintf(stderr, "%s [options] in.I32 in.spikes in.scale in.filter in.svm out.singlefish out.prob\n",
            progname);
    fprintf(stderr, "options:\n"
            "  -a|--onlyabove=a    Only analyze with SVM if above this amplitude\n"
            "  -z|--saturation=a,b Low and high saturation levels to filter out\n"
            "  -w|--minwins=w      Minimum windows needed to analyze with SVM\n"
            "  -p|--minprob=p      Minimum SVM probability to consider as single-fish\n"
            "  -d|--maxdist=d      Maximum distance to the next or previous spike\n"
            "  -s|--maxsize=s      Maximum size of a single-fish spike window\n");
    return 1;
}

int main(int argc, char **argv)
{
    commonInit();

    float onlyabove = defaultOnlyAbove;
    float saturationLow = defaultSaturationLow;
    float saturationHigh = defaultSaturationHigh;
    int minwins = defaultSingleMinWins;
    float minprob = defaultSingleMinProb;
    int maxdist = defaultSingleMaxDist;
    int maxsize = EODSamples;

    static float minval[NumFeatures] ALIGN(16);
    static float maxval[NumFeatures] ALIGN(16);

    while(1) {
        int option_index = 0;
        static struct option long_options[] = {
            { "onlyabove",  required_argument, 0, 'a' },
            { "saturation", required_argument, 0, 'z' },
            { "minwins",    required_argument, 0, 'w' },
            { "minprob",    required_argument, 0, 'p' },
            { "maxdist",    required_argument, 0, 'd' },
            { "maxsize",    required_argument, 0, 's' },
            { 0, 0, 0, 0 }
        };

        int c = getopt_long(argc, argv, "a:z:w:p:d:s:",
                            long_options, &option_index);
        if(c == -1)
            break;

        switch(c) {
        case 'a':
            onlyabove = QString(optarg).toFloat();
            break;
        case 'z':
        {
            QStringList sl = QString(optarg).split(",");
            if(sl.count() != 2) {
                fprintf(stderr, "--saturation argument must be  a list of two numbers\n");
                return 1;
            }
            saturationLow = sl.at(0).toFloat();
            saturationHigh = sl.at(1).toFloat();
        }
        case 'w':
            minwins = QString(optarg).toInt();
            break;
        case 'p':
            minprob = QString(optarg).toFloat();
            break;
        case 'd':
            maxdist = QString(optarg).toInt();
            break;
        case 's':
            maxsize = QString(optarg).toInt();
            break;
        default:
            return usage(argv[0]);
        }
    }

    if(argc - optind != 7)
        return usage(argv[0]);

    SignalFile sigfile(argv[optind]);
    if(!sigfile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "Can't open input data file (%s).\n", argv[optind]);
        return 1;
    }

    WindowFile winfile(argv[optind+1]);
    if(!winfile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "Can't open input spike file (%s).\n", argv[optind+1]);
        return 1;
    }

    QFile scalefile(argv[optind+2]);
    if(!scalefile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "Can't open feature scale file (%s).\n", argv[optind+2]);
        return 1;
    }
    readScaleFile(scalefile, minval, maxval);
    scalefile.close();

    QFile filterfile(argv[optind+3]);
    if(!filterfile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "Can't open feature filter file (%s).\n", argv[optind+3]);
        return 1;
    }
    FeatureFilter feafilter(filterfile);
    filterfile.close();

    svm_model *model = svm_load_model(argv[optind+4]);
    if(model == NULL) {
        fprintf(stderr, "Can't open SVM model file (%s).\n", argv[optind+4]);
        return 1;
    }

    QFile outfile(argv[optind+5]);
    if(!outfile.open(QIODevice::WriteOnly)) {
        fprintf(stderr, "Can't open output file (%s).\n", argv[optind+5]);
        return 1;
    }

    QFile completeoutfile(argv[optind+6]);
    if(!completeoutfile.open(QIODevice::WriteOnly)) {
        fprintf(stderr, "Can't open probability output file (%s).\n", argv[optind+5]);
        return 1;
    }

    findSingleFish(sigfile, winfile, minval, maxval,
                   feafilter, model, outfile, completeoutfile, onlyabove,
                   saturationLow, saturationHigh,
                   minwins, minprob, maxdist, maxsize);

    sigfile.close();
    winfile.close();
    outfile.close();
    completeoutfile.close();
    svm_free_and_destroy_model(&model);

    return 0;
}
