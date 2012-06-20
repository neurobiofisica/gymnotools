#ifndef SIGCFG_H
#define SIGCFG_H

/*
 * Base settings
 */

static const int NumChannels = 7;
static const int SamplingRate = 50000;
static const int EODSamples = 128;

/*
 * Derived settings
 */

static const int BytesPerSample = NumChannels * sizeof(float);


#endif // SIGCFG_H
