#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>

#include <QString>
#include <QStringList>
#include <QtAlgorithms>

#include "common/commoninit.h"
#include "common/windowfile.h"
#include "svm/svm.h"

static qint64 countWins(WindowFile &file)
{
    qint64 numWins = 0;
    while(file.nextEvent())
        numWins += file.getEventChannels();
    file.rewind();
    return numWins;
}

struct SVMProblem : svm_problem
{
    SVMProblem(WindowFile &trainA, WindowFile &trainB)
    {
    }
};

static void cmd_optim(WindowFile &trainA, WindowFile &trainB,
                      WindowFile &crossA, WindowFile &crossB,
                      double cStart, double cStop, double cStep,
                      double gStart, double gStop, double gStep)
{

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
        double cStart = -5., cStop =  15., cStep =  2.;
        double gStart =  3., gStop = -15., gStep = -2.;

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
    }
    else if(!strcmp(argv[1], "train")) {

    }
    else if(!strcmp(argv[1], "test")) {

    }
    else return usage(progname);

    return 0;
}
