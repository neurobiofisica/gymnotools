#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <assert.h>
#include <limits>

#include <omp.h>

#include <QString>
#include <QStringList>
#include <QTextStream>
#include <QList>
#include <QPair>
#include <QtAlgorithms>

#include "common/compilerspecific.h"
#include "common/commoninit.h"
#include "common/windowfile.h"
#include "common/sigcfg.h"
#include "common/sigutil.h"

struct CrossModel {
    float A[EODSamples] ALIGN(16);
    float B[EODSamples] ALIGN(16);

    void normA() { normalizeAbsAlignedFloat(A, EODSamples); }
    void normB() { normalizeAbsAlignedFloat(B, EODSamples); }

    bool load(const char *filename)
    {
        QFile file(filename);
        if(!file.open(QIODevice::ReadOnly))
            return false;
        file.read((char*)A, sizeof(A));
        file.read((char*)B, sizeof(B));
        file.close();
        return true;
    }

    void save(const char *filename)
    {
        QFile file(filename);
        file.open(QIODevice::WriteOnly);
        file.write((char*)A, sizeof(A));
        file.write((char*)B, sizeof(B));
        file.close();
    }
};

static qint64 countWins(WindowFile &file)
{
    qint64 numWins = 0;
    while(file.nextEvent())
        numWins += file.getEventChannels();
    file.rewind();
    return numWins;
}

static AINLINE double maxCrossCorrelation(const afloat *pattern, const afloat *window)
{
    // pattern length: EODSamples, window length: 3*EODSamples (zero fill)
    double maxCross = 0.;
    for(int i = 0; i <= 2*EODSamples; i++) {
        double cross = 0.;
        for(int j = 0; j < EODSamples; j++)
            cross += pattern[j]*window[i+j];

        cross = fabs(cross);
        if(cross > maxCross)
            maxCross = cross;
    }
    return maxCross;
}

static AINLINE double decisionValue(const CrossModel &model, const afloat *window)
{
    const double a = maxCrossCorrelation(model.A, window);
    const double b = maxCrossCorrelation(model.B, window);
    return a - b;
}

static void predictAndCount(const CrossModel &model, WindowFile &file, int &nA, int &nB, afloat *buf)
{
    nA = nB = 0;
    while(file.nextChannel()) {
        assert(file.getEventSamples() == EODSamples);
        file.read((char*)&buf[EODSamples], EODSamples*sizeof(float));
        if(decisionValue(model, buf) >= 0.)
            nA++;
        else
            nB++;
    }
    file.rewind();
}

static AINLINE void predictAndCount(const CrossModel &model, WindowFile &file, int &nA, int &nB)
{
    static float buf[3*EODSamples] ALIGN(16) = { 0. };
    predictAndCount(model, file, nA, nB, buf);
}

static int countErrors(const CrossModel &model, WindowFile &crossA, WindowFile &crossB)
{
    static float bufA[3*EODSamples] ALIGN(16) = { 0. };
    static float bufB[3*EODSamples] ALIGN(16) = { 0. };
    int errorsA, errorsB;
#pragma omp parallel sections
    {
#pragma omp section
        {
            int nA = 0, nB = 0;
            predictAndCount(model, crossA, nA, nB, bufA);
            errorsA = nB;
        }
#pragma omp section
        {
            int nA = 0, nB = 0;
            predictAndCount(model, crossB, nA, nB, bufB);
            errorsB = nA;
        }
    }
    return errorsA + errorsB;
}

typedef QPair<int,int> IntPair;

static void cmd_optim(WindowFile &trainA, WindowFile &trainB,
                      WindowFile &crossA, WindowFile &crossB)
{
    static CrossModel model ALIGN(16);
    const int numA = countWins(trainA), numB = countWins(trainB);
    const double percentFactorTrain = 100./(((double)numA) * numB);
    const double percentFactorCross = 100./(countWins(crossA) + countWins(crossB));

    printf("=> Trying all (A,B) window pairs...\n");

    int bestErr = std::numeric_limits<int>::max();
    IntPair bestij(-1, -1);
    qint64 cont = 0;

    for(int i = 1; i <= numA; i++) {
        bool hasNext = trainA.nextChannel();
        assert(hasNext);
        assert(trainA.getEventSamples() == EODSamples);
        trainA.read((char*)model.A, EODSamples*sizeof(float));
        model.normA();

        trainB.rewind();
        for(int j = 1; j <= numB; j++) {
            bool hasNext = trainB.nextChannel();
            assert(hasNext);
            assert(trainB.getEventSamples() == EODSamples);
            trainB.read((char*)model.B, EODSamples*sizeof(float));
            model.normB();

            const int err = countErrors(model, crossA, crossB);
            if(err < bestErr) {
                bestErr = err;
                bestij = IntPair(i, j);
            }

            printf("\r%8.3f%%  (bestErr: %7d, A: %5d, B: %5d)        ",
                   (cont++)*percentFactorTrain,
                   bestErr, bestij.first, bestij.second);
            fflush(stdout);
        }
    }

    printf("\n=> Best (A,B): %5d %5d\n", bestij.first, bestij.second);
    printf("=> Number of errors: %d (%.2f%%)\n", bestErr, bestErr*percentFactorCross);
}

static void cmd_train(const char *modelfile, int Apat, int Bpat,
                      WindowFile &trainA, WindowFile &trainB)
{
    static CrossModel model ALIGN(16);

    for(int i = 0; i < Apat && trainA.nextChannel(); i++);
    assert(trainA.getEventSamples() == EODSamples);
    trainA.read((char*)model.A, EODSamples*sizeof(float));
    model.normA();

    for(int i = 0; i < Bpat && trainB.nextChannel(); i++);
    assert(trainB.getEventSamples() == EODSamples);
    trainB.read((char*)model.B, EODSamples*sizeof(float));
    model.normB();

    model.save(modelfile);
}

static void cmd_test_count(const CrossModel &model, WindowFile &testFile)
{
    int nA = 0, nB = 0;
    predictAndCount(model, testFile, nA, nB);
    double total = nA + nB;
    printf("A: %d (%.2f%%)\n", nA, (100.*nA)/total);
    printf("B: %d (%.2f%%)\n", nB, (100.*nB)/total);
}

static void cmd_test_list(const CrossModel &model, WindowFile &testFile)
{
    QTextStream ts(stdout);
    const QString fmt("%1: decision { %2 } @ %3 ch %4\n");
    static float buf[3*EODSamples] ALIGN(16) = { 0. };

    while(testFile.nextChannel()) {
        assert(testFile.getEventSamples() == EODSamples);
        testFile.read((char*)&buf[EODSamples], EODSamples*sizeof(float));

        double decision = decisionValue(model, buf);
        const char subj = (decision >= 0.) ? 'A' : 'B';
        const double t = (testFile.getEventOffset() / BytesPerSample)/
                (double)SamplingRate;

        ts << fmt.arg(subj)
                .arg(decision, 0, 'f', 4)
                .arg(t, 0, 'f', 6)
                .arg(testFile.getChannelId());
    }
}

typedef QPair<double,int> DecisionLabel;

static void populateDecisionLabelPairs(const CrossModel &model, QList<DecisionLabel> &list,
                                       WindowFile &file, int label)
{
    static float buf[3*EODSamples] ALIGN(16) = { 0. };

    while(file.nextChannel()) {
        assert(file.getEventSamples() == EODSamples);
        file.read((char*)&buf[EODSamples], EODSamples*sizeof(float));
        list.append(DecisionLabel(-decisionValue(model, buf), label));
    }

    file.rewind();
}

static void cmd_roc(const CrossModel &model, WindowFile &testA, WindowFile &testB)
{
    QList<DecisionLabel> list;
    populateDecisionLabelPairs(model, list, testA, +1);
    populateDecisionLabelPairs(model, list, testB, -1);
    qSort(list);

    double positiveLabels = countWins(testA);
    double negativeLabels = countWins(testB);

    double truePositives = 0., falsePositives = 0.;

    foreach(const DecisionLabel &pair, list) {
        if(pair.second > 0)
            truePositives  += 1.;
        else
            falsePositives += 1.;

        printf("%.12f %.12f\n",
               falsePositives/negativeLabels,
               truePositives/positiveLabels);
    }
}

static int usage(const char *progname)
{
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "%s optim A.spikes B.spikes crossA.spikes crossB.spikes\n"
            "  Find the best patterns for training a cross-correlation model to tell A and B\n"
            "  subjects apart. Use crossA.features and crossB.features to construct the\n"
            "  cross-validation set.\n", progname);
    fprintf(stderr, "%s train cross.model A-pattern B-pattern A.spikes B.spikes"
            "  Train a model using the given training set and A and B patterns.\n", progname);
    fprintf(stderr, "%s test [count|list] cross.model file.spikes"
            "  Classify the features contained in the file in order to test a model.\n"
            "  If 'count' is asked, only counts the number of A and B results.\n"
            "  If 'list' is asked, outputs a list of results with probability estimators.\n",
            progname);
    fprintf(stderr, "%s roc cross.model testA.features testB.spikes"
            "  Outputs a list of FAR (false A rate) and TAR (true A rate) values,\n"
            "  which can be used to plot a ROC curve.\n", progname);
    return 1;
}

int main(int argc, char **argv)
{
    static CrossModel model ALIGN(16);
    const char *progname = argv[0];
    commonInit();

    if(argc < 2)
        return usage(progname);

    if(!strcmp(argv[1], "optim")) {
        if(argc != 6)
            return usage(progname);

        WindowFile trainA(argv[2]);
        if(!trainA.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind]);
            return 1;
        }
        WindowFile trainB(argv[3]);
        if(!trainB.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind+1]);
            return 1;
        }
        WindowFile crossA(argv[4]);
        if(!crossA.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind+2]);
            return 1;
        }
        WindowFile crossB(argv[5]);
        if(!crossB.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind+3]);
            return 1;
        }

        cmd_optim(trainA, trainB, crossA, crossB);

        trainA.close();
        trainB.close();
        crossA.close();
        crossB.close();
    }
    else if(!strcmp(argv[1], "train")) {
        if(argc != 7)
            return usage(progname);
        char *modelfile = argv[2];
        bool ok1 = false, ok2 = false;
        int Apat = QString(argv[3]).toInt(&ok1);
        int Bpat = QString(argv[4]).toInt(&ok2);
        if(!ok1 || !ok2) {
            fprintf(stderr, "invalid number passed as 'A-pattern' or 'B-pattern' parameter\n");
            return 1;
        }
        WindowFile trainA(argv[5]);
        if(!trainA.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[5]);
            return 1;
        }
        WindowFile trainB(argv[6]);
        if(!trainB.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[6]);
            return 1;
        }
        cmd_train(modelfile, Apat, Bpat, trainA, trainB);
        trainA.close();
        trainB.close();
    }
    else if(!strcmp(argv[1], "test")) {
        if(argc != 5)
            return usage(progname);

        if(!model.load(argv[3])) {
            fprintf(stderr, "can't open model file '%s' for reading\n", argv[3]);
            return 1;
        }
        WindowFile testFile(argv[4]);
        if(!testFile.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[4]);
            return 1;
        }
        if(!strcmp(argv[2], "count"))
            cmd_test_count(model, testFile);
        else if(!strcmp(argv[2], "list"))
            cmd_test_list(model, testFile);
        else return usage(progname);
        testFile.close();
    }
    else if(!strcmp(argv[1], "roc")) {
        if(argc != 5)
            return usage(progname);
        if(!model.load(argv[2])) {
            fprintf(stderr, "can't open model file '%s' for reading\n", argv[2]);
            return 1;
        }
        WindowFile testA(argv[3]);
        if(!testA.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[3]);
            return 1;
        }
        WindowFile testB(argv[4]);
        if(!testB.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[4]);
            return 1;
        }
        cmd_roc(model, testA, testB);
        testA.close();
        testB.close();
    }
    else return usage(progname);

    return 0;
}
