#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <QApplication>
#include <QString>
#include <QMessageBox>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "sigparamselectiondialog.h"
#include "fileminmaxfinder.h"

static const char *progname = "paramchooser";
static int usage();

static int lowpass_main(int argc, char **argv) {
    if(argc != 2)
        return usage();
    SigParamLowpassDialog *dlg = new SigParamLowpassDialog(
                argv[1],
                defaultLowpassNumTaps,
                defaultLowPassCutoff);
    if(dlg->exec()) {
        printf("numtaps = %d\n", dlg->sbTaps->value() | 1);
        printf("cutoff = %.2f\n", dlg->sbCutoff->value());
    }
    delete dlg;
    return 0;
}

static int threshold_main(int argc, char **argv) {
    if(argc != 4)
        return usage();
    SigParamThresholdDialog *dlg = new SigParamThresholdDialog(
                argv[1],
                QString(argv[2]).toInt(),
                QString(argv[3]).toFloat(),
                defaultDetectionThreshold);
    if(dlg->exec()) {
        printf("threshold = %.4f\n", dlg->sbThreshold->value());
    }
    delete dlg;
    return 0;
}

static int amplitude_threshold_main(int argc, char **argv) {
    if(argc != 2)
        return usage();
    SigParamAmplitudeDialog *dlg = new SigParamAmplitudeDialog(
                argv[1],
                defaultOnlyAbove);
    if(dlg->exec()) {
        printf("amplitude_threshold = %.2f\n", dlg->sbThreshold->value());
    }
    delete dlg;
    return 0;
}

static int saturation_main(int argc, char **argv) {
    if(argc != 2 && argc != 3)
        return usage();

    float ratio = 0.95;
    if(argc == 3)
        ratio = QString(argv[2]).toFloat();

    float min, max;
    if(!FileMinMaxFinder::getMinMax(NULL, argv[1], min, max)) {
        QMessageBox::critical(NULL, "Problem reading file", "Can't find the minimum and maximum "
                              "sample values contained in the data file.");
        return 1;
    }

    SigParamSaturationDialog *dlg = new SigParamSaturationDialog(
                argv[1],
                defaultSaturationLow,
                defaultSaturationHigh,
                ratio*min,
                ratio*max);
    if(dlg->exec()) {
        printf("saturation_low = %.2f\n", dlg->sbThresholdL->value());
        printf("saturation_high = %.2f\n", dlg->sbThresholdH->value());
    }
    delete dlg;
    return 0;
}

struct module_t {
    const char *name;
    const char *arghelp;
    int (*main)(int argc, char **argv);
};

module_t modules[] = {
    {"lowpass", "datafile", lowpass_main},
    {"threshold", "datafile numtaps cutoff", threshold_main},
    {"amplitude_threshold", "datafile", amplitude_threshold_main},
    {"saturation", "datafile [search_ratio]", saturation_main},
    {NULL, NULL, NULL}
};

static int usage() {
    fprintf(stderr, "usage: %s module [arguments]\n", progname);
    fprintf(stderr, "available modules:\n");
    for(int i = 0; modules[i].name != NULL; i++) {
        fprintf(stderr, "  %s %s\n", modules[i].name, modules[i].arghelp);
    }
    return 1;
}

int main(int argc, char **argv)
{
    QApplication *app = new QApplication(argc, argv);
    commonInit();
    progname = argv[0];

    if(argc >= 2) {
        for(int i = 0; modules[i].name != NULL; i++) {
            if(!strcasecmp(argv[1], modules[i].name)) {
                return modules[i].main(argc - 1, &argv[1]);
            }
        }
    }

    delete app;
    return usage();
}
