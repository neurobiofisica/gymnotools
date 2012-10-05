#ifndef DEFAULTPARAMS_H
#define DEFAULTPARAMS_H

static const int   defaultLowpassNumTaps = 11;
static const float defaultLowPassCutoff = 0.10;
static const float defaultDetectionThreshold = 0.0600;
static const float defaultMinLevel = 0.0012;
static const float defaultMinRatio = 0.00037;
static const int   defaultStopSamples = 16;
static const float defaultOnlyAbove = 0.85;
static const float defaultSaturationLow = -8.44;
static const float defaultSaturationHigh = 8.05;

static const int   defaultStormGlue = 32;
static const int   defaultStormSize = 256;
static const int   defaultStormAfterGlue = 500;

static const int   defaultSingleMinWins = 3;
static const float defaultSingleMinProb = 0.95;
static const int   defaultSingleMaxDist = 10000000;

static const int   defaultRecogFillSamples = 3;
static const float defaultRecogISIWindow = .1;
static const float defaultRecogDistFactor = .1;

#endif // DEFAULTPARAMS_H
