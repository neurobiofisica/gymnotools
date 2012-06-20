#ifndef GUICFG_H
#define GUICFG_H

#include "common/sigcfg.h"

/*
 * Base settings
 */

static const float MaxAmplitude = 10.;
static const int PlotDialogNumPoints = 25000;
static const int EODsPerWindow = 15;

/*
 * Derived settings
 */

static const int CurvesPerWindow = EODsPerWindow * NumChannels;

#endif // GUICFG_H
