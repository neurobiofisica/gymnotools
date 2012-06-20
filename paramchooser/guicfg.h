#ifndef PARAMCHOOSER_GUICFG_H
#define PARAMCHOOSER_GUICFG_H

#include "common/sigcfg.h"

/*
 * Base settings
 */

static const float MaxAmplitude = 10.;
static const int EODsPerWindow = 15;

/*
 * Derived settings
 */

static const int CurvesPerWindow = EODsPerWindow * NumChannels;

#endif // PARAMCHOOSER_GUICFG_H
