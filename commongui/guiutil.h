#ifndef GUIUTIL_H
#define GUIUTIL_H

#include <QtGlobal>

#include "common/compilerspecific.h"
#include "guicfg.h"

static AINLINE void fillXData(double *xdata, qint64 curPos) {
    for(int i = 0; i < PlotDialogNumPoints; i++)
        xdata[i] = (curPos/(double)BytesPerSample + i)/(double)SamplingRate;
}

#endif // GUIUTIL_H
