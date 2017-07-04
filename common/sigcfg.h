#ifndef SIGCFG_H
#define SIGCFG_H

/*
 * Base settings
 */

static const int NumChannels = 8;
static const double SamplingRate = 50000.0;
static const int EODSamples = 512;

/*
 * Derived settings
 */

static const int BytesPerSample = NumChannels * sizeof(float);


#endif // SIGCFG_H
