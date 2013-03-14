#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <assert.h>
#include <limits>

#include <QString>
#include <QStringList>
#include <QList>
#include <QPair>
#include <QtAlgorithms>

#include "common/compilerspecific.h"
#include "common/commoninit.h"
#include "common/windowfile.h"
#include "common/sigcfg.h"

struct CrossModel {
    float A[EODSamples] ALIGN(16);
    float B[EODSamples] ALIGN(16);

    bool load(const char *filename) {
        QFile file(filename);
        if(!file.open(QIODevice::ReadOnly))
            return false;
        file.read((char*)A, sizeof(A));
        file.read((char*)B, sizeof(B));
        file.close();
        return true;
    }

    void save(const char *filename) {
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

static AINLINE double decisionValue(const CrossModel *model, const afloat *window)
{
    const double a = maxCrossCorrelation(model->A, window);
    const double b = maxCrossCorrelation(model->B, window);
    if(a >= b)
        return a;
    return -b;
}

static void predictAndCount(const CrossModel *model, WindowFile &file, int &nA, int &nB)
{
    static float buf[3*EODSamples] ALIGN(16) = { 0. };

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

static int countErrors(CrossModel *model, WindowFile &crossA, WindowFile &crossB)
{
    int errors = 0;
    int nA = 0, nB = 0;
    predictAndCount(model, crossA, nA, nB);
    errors += nB;
    predictAndCount(model, crossB, nA, nB);
    errors += nA;
    return errors;
}

static void cmd_optim(WindowFile &trainA, WindowFile &trainB,
                      WindowFile &crossA, WindowFile &crossB)
{
}

static void cmd_train(const char *modelfile, int Apat, int Bpat,
                      WindowFile &trainA, WindowFile &trainB)
{
    CrossModel model;

    for(int i = 0; i <= Apat && trainA.nextChannel(); i++);
    assert(trainA.getEventSamples() == EODSamples);
    trainA.read((char*)model.A, EODSamples*sizeof(float));

    for(int i = 0; i <= Bpat && trainB.nextChannel(); i++);
    assert(trainB.getEventSamples() == EODSamples);
    trainA.read((char*)model.B, EODSamples*sizeof(float));

    model.save(modelfile);
}

static void cmd_test_count(CrossModel *model, WindowFile &testFile)
{
    int nA = 0, nB = 0;
    predictAndCount(model, testFile, nA, nB);
    double total = nA + nB;
    printf("A: %d (%.2f%%)\n", nA, (100.*nA)/total);
    printf("B: %d (%.2f%%)\n", nB, (100.*nB)/total);
}

static void cmd_test_list(CrossModel *model, WindowFile &testFile)
{
    const QString fmt("%1: decision { %2 } @ %3 ch %4\n");
    static float buf[3*EODSamples] ALIGN(16) = { 0. };

    while(testFile.nextChannel()) {
        assert(testFile.getEventSamples() == EODSamples);
        testFile.read((char*)&buf[EODSamples], EODSamples*sizeof(float));

        double decision = decisionValue(model, buf);
        const char subj = (decision >= 0.) ? 'A' : 'B';
        const double t = (testFile.getEventOffset() / BytesPerSample)/
                (double)SamplingRate;

        fputs(fmt.arg(subj)
                .arg(decision, 0, 'f', 4)
                .arg(t, 0, 'f', 6)
                .arg(testFile.getChannelId())
                .toAscii(), stdout);
    }
}

typedef QPair<double,int> DecisionLabel;

static void populateDecisionLabelPairs(CrossModel *model, QList<DecisionLabel> &list,
                                       WindowFile &file, int label)
{
    static float buf[3*EODSamples] ALIGN(16) = { 0. };

    while(file.nextChannel()) {
        assert(file.getEventSamples() == EODSamples);
        file.read((char*)&buf[EODSamples], EODSamples*sizeof(float));
        list.append(DecisionLabel(decisionValue(model, buf), label));
    }

    file.rewind();
}

static void cmd_roc(CrossModel *model, WindowFile &testA, WindowFile &testB)
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
    fprintf(stderr, "%s optim A.features B.features crossA.features crossB.features\n"
            "  Find the best patterns for training a cross-correlation model to tell A and B\n"
            "  subjects apart. Use crossA.features and crossB.features to construct the\n"
            "  cross-validation set.\n", progname);
    fprintf(stderr, "%s train cross.model A-pattern B-pattern A.features B.features\n"
            "  Train a model using the given training set and A and B patterns.\n", progname);
    fprintf(stderr, "%s test [count|list] cross.model file.features\n"
            "  Classify the features contained in the file in order to test a model.\n"
            "  If 'count' is asked, only counts the number of A and B results.\n"
            "  If 'list' is asked, outputs a list of results with probability estimators.\n",
            progname);
    fprintf(stderr, "%s roc cross.model testA.features testB.features\n"
            "  Outputs a list of FAR (false A rate) and TAR (true A rate) values,\n"
            "  which can be used to plot a ROC curve.\n", progname);
    return 1;
}

int main(int argc, char **argv)
{
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
        CrossModel model;
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
            cmd_test_count(&model, testFile);
        else if(!strcmp(argv[2], "list"))
            cmd_test_list(&model, testFile);
        else return usage(progname);
        testFile.close();
    }
    else if(!strcmp(argv[1], "roc")) {
        if(argc != 5)
            return usage(progname);
        CrossModel model;
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
        cmd_roc(&model, testA, testB);
        testA.close();
        testB.close();
    }
    else return usage(progname);

    return 0;
}
