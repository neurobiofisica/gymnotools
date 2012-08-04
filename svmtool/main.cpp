#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <assert.h>
#include <limits>

#include <QString>
#include <QStringList>
#include <QtAlgorithms>

#include "common/compilerspecific.h"
#include "common/commoninit.h"
#include "common/windowfile.h"
#include "common/svmutil.h"
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

static AINLINE void fillNodes(svm_node *nodes, const float *buf, int samples)
{
    for(int i = 0; i < samples; i++) {
        nodes[i].index = i + 1;
        nodes[i].value = buf[i];
    }
    nodes[samples].index = -1;
}

struct SVMProblem : svm_problem
{
    SVMProblem(WindowFile &trainA, WindowFile &trainB)
    {
        l = countWins(trainA) + countWins(trainB);

        const qint32 samples = getNumSamples(trainA);
        assert(getNumSamples(trainB) == samples);

        y = new double[l];
        x = new svm_node*[l];
        x[0] = new svm_node[l*(samples+1)];
        for(int i = 1; i < l; i++) {
            x[i] = &x[i-1][samples+1];
        }

        float *buf = new float[samples];
        int cur = 0;

        while(trainA.nextChannel()) {
            assert(trainA.getEventSamples() == samples);
            trainA.read((char*)buf, samples*sizeof(float));
            fillNodes(x[cur], buf, samples);
            y[cur++] = 1.;
        }

        while(trainB.nextChannel()) {
            assert(trainB.getEventSamples() == samples);
            trainB.read((char*)buf, samples*sizeof(float));
            fillNodes(x[cur], buf, samples);
            y[cur++] = -1.;
        }

        delete[] buf;
        assert(cur == l);
    }
    ~SVMProblem()
    {
        delete[] x[0];
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

    int bestErrors = problem.l;
    double bestg = 0., bestc = 0.;

    const double eps = std::numeric_limits<float>::epsilon();

    for(double g = gStart; g <= gStop; g += gStep) {
        for(double c = cStart; c <= cStop; c += cStep) {
            printf("=> Trying c=%.1f, g=%.1f\n", c, g);
            param.setcg(c, g);

            svm_model *model = svm_train(&problem, &param);
            const int errors = countErrors(model, crossA, crossB);
            svm_free_and_destroy_model(&model);

            printf("=> Errors: %d\n", errors);
            if((errors  < bestErrors) || (errors == bestErrors && fabs(g-bestg)<=eps && c<bestc)) {
                bestErrors = errors;
                bestc = c;
                bestg = g;
            }
        }
    }

    printf("\n\n=> Best: c=%.1f, g=%.1f\n", bestc, bestg);
    printf("=> Errors: %d (%.2f%%)\n", bestErrors, (100.*bestErrors)/problem.l);
}

static void cmd_train(char *modelfile, double cParam, double gParam,
                      WindowFile &trainA, WindowFile &trainB)
{
    SVMProblem problem(trainA, trainB);
    SVMParam param(cParam, gParam, true);
    svm_model *model = svm_train(&problem, &param);
    svm_save_model(modelfile, model);
    svm_free_and_destroy_model(&model);
}

static void cmd_test(char *modelfile, WindowFile &testFile)
{
    svm_model *model = svm_load_model(modelfile);
    int nA = 0, nB = 0;
    predictAndCount(model, testFile, nA, nB);
    svm_free_and_destroy_model(&model);
    double total = nA + nB;
    printf("A: %d (%.2f%%)\n", nA, (100.*nA)/total);
    printf("B: %d (%.2f%%)\n", nB, (100.*nB)/total);
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
            "  Train a SVM using the given test set and 'c' and 'g' parameters.\n", progname);
    fprintf(stderr, "%s test svm.model file.features\n"
            "  Classify the features contained in the file in order to test a SVM model.\n",
            progname);
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
    else if(!strcmp(argv[1], "test")) {
        if(argc != 4)
            return usage(progname);
        char *modelfile = argv[2];
        WindowFile testFile(argv[3]);
        if(!testFile.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "can't open feature file '%s' for reading\n", argv[3]);
            return 1;
        }
        cmd_test(modelfile, testFile);
        testFile.close();
    }
    else return usage(progname);

    return 0;
}
