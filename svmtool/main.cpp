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
#include "common/svmutil.h"
#include "common/sigcfg.h"
#include "svm/svm.h"

static qint64 countWins(WindowFile &file)
{
    qint64 numWins = 0;
    while(file.nextEvent())
        numWins += file.getEventChannels();
    file.rewind();
    return numWins;
}

static AINLINE qint32 getNumSamples(WindowFile &file)
{
    bool hasEvents = file.nextEvent();
    assert(hasEvents);
    qint32 samples = file.getEventSamples();
    return samples;
}

static AINLINE void fillNode(svm_node &node, const float *buf, int samples)
{
    for(int i = 0; i < samples; i++)
        node.values[i] = buf[i];
    node.dim = samples;
}

struct SVMProblem : svm_problem
{
    SVMProblem(WindowFile &trainA, WindowFile &trainB)
    {
        l = countWins(trainA) + countWins(trainB);

        const qint32 samples = getNumSamples(trainA);
        assert(getNumSamples(trainB) == samples);

        y = new double[l];
        x = new svm_node[l];
        x[0].values = new double[l*samples];
        for(int i = 1; i < l; i++)
            x[i].values = &x[i-1].values[samples];

        float *buf = new float[samples];
        int cur = 0;

        while(trainA.nextChannel()) {
            assert(trainA.getEventSamples() == samples);
            trainA.read((char*)buf, samples*sizeof(float));
            fillNode(x[cur], buf, samples);
            y[cur++] = 1.;
        }

        while(trainB.nextChannel()) {
            assert(trainB.getEventSamples() == samples);
            trainB.read((char*)buf, samples*sizeof(float));
            fillNode(x[cur], buf, samples);
            y[cur++] = -1.;
        }

        delete[] buf;
        assert(cur == l);
    }
    ~SVMProblem()
    {
        delete[] x[0].values;
        delete[] x;
        delete[] y;
    }
};

struct SVMParam : svm_parameter
{
    SVMParam() { init(); }
    SVMParam(double cParam, double gParam, bool probab = false)
    {
        init();
        setcg(cParam, gParam);
        probability = probab ? 1 : 0;
    }
    void setcg(double cParam, double gParam)
    {
        C     = pow(2., cParam);
        gamma = pow(2., gParam);
    }
private:
    void init()
    {
        svm_type = C_SVC;
        kernel_type = RBF;
        degree = 3;
        coef0 = 0;
        nu = 0.5;
        cache_size = 100;
        eps = 1e-3;
        p = 0.1;
        shrinking = 0;
        probability = 0;
        nr_weight = 0;
        weight_label = NULL;
        weight = NULL;
    }
};

static void predictAndCount(svm_model *model, WindowFile &file, int &nA, int &nB)
{
    const qint32 samples = getNumSamples(file);
    float *buf = new float[samples];
    SVMNodeList nodelist(samples);

    nA = nB = 0;

    while(file.nextChannel()) {
        assert(file.getEventSamples() == samples);
        file.read((char*)buf, samples*sizeof(float));
        nodelist.fill(buf);
        if(svm_predict(model, nodelist) > 0)
            ++nA;
        else
            ++nB;
    }

    delete[] buf;
    file.rewind();
}

static int countErrors(svm_model *model, WindowFile &crossA, WindowFile &crossB)
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
                      WindowFile &crossA, WindowFile &crossB,
                      double cStart, double cStop, double cStep,
                      double gStart, double gStop, double gStep)
{
    SVMProblem problem(trainA, trainB);
    SVMParam param;

    const int totalWins = crossA.getNumEventsAndNumWins().second + crossB.getNumEventsAndNumWins().second;
    int bestErrors = totalWins;
    double bestg = 0., bestc = 0.;

    const double eps = std::numeric_limits<float>::epsilon();

    for(double g = gStart; g <= gStop; g += gStep) {
        for(double c = cStart; c <= cStop; c += cStep) {
            fprintf(stderr, "=> Trying c=%.1f, g=%.1f\n", c, g);
            param.setcg(c, g);

            svm_model *model = svm_train(&problem, &param);
            const int errors = countErrors(model, crossA, crossB);
            svm_free_and_destroy_model(&model);

            fprintf(stderr, "=> Errors: %d\n", errors);
            if((errors  < bestErrors) || (errors == bestErrors && fabs(g-bestg)<=eps && c<bestc)) {
                bestErrors = errors;
                bestc = c;
                bestg = g;
            }
        }
    }

    fprintf(stderr, "\n\n=> Best: c=%.1f, g=%.1f\n", bestc, bestg);
    fprintf(stderr, "=> Errors: %d (%.2f%%)\n", bestErrors, (100.*bestErrors)/totalWins);
}

static void cmd_train(const char *modelfile, double cParam, double gParam,
                      WindowFile &trainA, WindowFile &trainB)
{
    SVMProblem problem(trainA, trainB);
    SVMParam param(cParam, gParam, true);
    svm_model *model = svm_train(&problem, &param);
    svm_save_model(modelfile, model);
    svm_free_and_destroy_model(&model);
}


static void cmd_cross(int nFold, double cParam, double gParam,
                      WindowFile &trainA, WindowFile &trainB)
{
    SVMProblem problem(trainA, trainB);
    SVMParam param(cParam, gParam);
    double *target = new double[problem.l];
    svm_cross_validation(&problem, &param, nFold, target);

    int correct = 0;
    for(int i = 0; i < problem.l; i++)
        if(target[i] == problem.y[i])
            ++correct;

    delete [] target;

    fprintf(stderr, "Cross Validation Accuracy = %g%%\n",(100.*correct)/problem.l);
}

static void cmd_test_count(svm_model *model, WindowFile &testFile)
{
    int nA = 0, nB = 0;
    predictAndCount(model, testFile, nA, nB);
    double total = nA + nB;
    fprintf(stderr, "A: %d (%g%%)\n", nA, (100.*nA)/total);
    fprintf(stderr, "B: %d (%g%%)\n", nB, (100.*nB)/total);
}

static void cmd_test_list(svm_model *model, WindowFile &testFile)
{
    const QString fmt("%1: prob { %2 , %3 } @ %4 ch %5\n");

    const qint32 samples = getNumSamples(testFile);
    float *buf = new float[samples];
    SVMNodeList nodelist(samples);
    double probEstim[2];

    while(testFile.nextChannel()) {
        assert(testFile.getEventSamples() == samples);
        testFile.read((char*)buf, samples*sizeof(float));
        nodelist.fill(buf);

        const char subj =
                (svm_predict_probability(model, nodelist, probEstim) > 0)
                ? 'A' : 'B';

        const double t = (testFile.getEventOffset() / BytesPerSample)/
                (double)SamplingRate;

        fputs(fmt.arg(subj)
                .arg(probEstim[0], 0, 'f', 4)
                .arg(probEstim[1], 0, 'f', 4)
                .arg(t, 0, 'f', 6)
                .arg(testFile.getChannelId())
                .toAscii(), stdout);
    }

    delete[] buf;
}

typedef QPair<double,int> DecisionLabel;

static void populateDecisionLabelPairs(svm_model *model, QList<DecisionLabel> &list,
                                       WindowFile &file, int label)
{
    const qint32 samples = getNumSamples(file);
    float *buf = new float[samples];
    SVMNodeList nodelist(samples);
    double decision = 0.;

    while(file.nextChannel()) {
        assert(file.getEventSamples() == samples);
        file.read((char*)buf, samples*sizeof(float));
        nodelist.fill(buf);
        svm_predict_values(model, nodelist, &decision);
        list.append(DecisionLabel(-decision, label));
    }

    delete[] buf;
    file.rewind();
}

static void cmd_roc(svm_model *model, WindowFile &testA, WindowFile &testB)
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

        fprintf(stderr, "%.12f %.12f\n",
               falsePositives/negativeLabels,
               truePositives/positiveLabels);
    }
}

static int usage(const char *progname)
{
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "%s optim [options] A.features B.features crossA.features crossB.features\n"
            "  Find the best 'c' and 'g' parameters for training a SVM to tell A and B\n"
            "  subjects apart. Use crossA.features and crossB.features to construct the\n"
            "  cross-validation set.\n"
            "  Available options:\n"
            "    -c start,stop,step   specify 'c' values to be tried\n"
            "    -g start,stop,step   specify 'g' values to be tried\n", progname);
    fprintf(stderr, "%s train svm.model c-param g-param A.features B.features\n"
            "  Train a SVM using the given training set and 'c' and 'g' parameters.\n", progname);
    fprintf(stderr, "%s cross n-fold c-param g-param A.features B.features\n"
            "  Do a true n-fold cross-validation.\n", progname);
    fprintf(stderr, "%s test [count|list] svm.model file.features\n"
            "  Classify the features contained in the file in order to test a SVM model.\n"
            "  If 'count' is asked, only counts the number of A and B results.\n"
            "  If 'list' is asked, outputs a list of results with probability estimators.\n",
            progname);
    fprintf(stderr, "%s roc svm.model testA.features testB.features\n"
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
        double cStart =  -5., cStop = 15., cStep = 2.;
        double gStart = -15., gStop =  3., gStep = 2.;

        argc -= 1;
        argv = &argv[1];

        while(1) {
            int opt = getopt(argc, argv, "c:g:");
            if(opt == -1)
                break;
            if(opt != 'c' && opt != 'g')
                return usage(progname);

            QStringList sl = QString(optarg).split(",");
            if(sl.count() != 3) {
                fprintf(stderr, "-c and -g options require a list of three numbers: start, stop and step\n");
                return 1;
            }

            bool ok1 = false, ok2 = false, ok3 = false;
            double optStart = sl.at(0).toDouble(&ok1);
            double optStop  = sl.at(1).toDouble(&ok2);
            double optStep  = sl.at(2).toDouble(&ok3);
            if(!ok1 || !ok2 || !ok3) {
                fprintf(stderr, "invalid numbers passed to -c or -g arguments\n");
                return 1;
            }

            if(opt == 'c') {
                cStart = optStart;
                cStop  = optStop;
                cStep  = optStep;
            }
            else if(opt == 'g') {
                gStart = optStart;
                gStop  = optStop;
                gStep  = optStep;
            }
        }

        if(argc - optind != 4)
            return usage(progname);

        WindowFile trainA(argv[optind]);
        if(!trainA.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind]);
            return 1;
        }
        WindowFile trainB(argv[optind+1]);
        if(!trainB.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind+1]);
            return 1;
        }
        WindowFile crossA(argv[optind+2]);
        if(!crossA.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind+2]);
            return 1;
        }
        WindowFile crossB(argv[optind+3]);
        if(!crossB.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[optind+3]);
            return 1;
        }

        cmd_optim(trainA, trainB, crossA, crossB,
                  cStart, cStop, cStep,
                  gStart, gStop, gStep);

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
        double cParam = QString(argv[3]).toDouble(&ok1);
        double gParam = QString(argv[4]).toDouble(&ok2);
        if(!ok1 || !ok2) {
            fprintf(stderr, "invalid number passed as 'c' or 'g' parameter\n");
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
        cmd_train(modelfile, cParam, gParam, trainA, trainB);
        trainA.close();
        trainB.close();
    }
    else if(!strcmp(argv[1], "cross")) {
        if(argc != 7)
            return usage(progname);
        bool ok1 = false, ok2 = false, ok3 = false;
        int nFold = QString(argv[2]).toInt(&ok1);
        double cParam = QString(argv[3]).toDouble(&ok2);
        double gParam = QString(argv[4]).toDouble(&ok3);
        if(!ok1 || !ok2 || !ok3) {
            fprintf(stderr, "invalid number passed as n-fold or 'c' or 'g' parameter\n");
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
        cmd_cross(nFold, cParam, gParam, trainA, trainB);
        trainA.close();
        trainB.close();
    }
    else if(!strcmp(argv[1], "test")) {
        if(argc != 5)
            return usage(progname);
        svm_model *model = svm_load_model(argv[3]);
        if(model == NULL) {
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
        svm_free_and_destroy_model(&model);
        testFile.close();
    }
    else if(!strcmp(argv[1], "roc")) {
        if(argc != 5)
            return usage(progname);
        svm_model *model = svm_load_model(argv[2]);
        if(model == NULL) {
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
