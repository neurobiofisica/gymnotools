#ifndef CUTINCOMPLETE_H
#define CUTINCOMPLETE_H

#include "signalfile.h"

/**
 * Cut spikes which are incomplete at the start or at the end of a signal file.
 * @param file the signal file
 * @param minlevel level below which signal is considered silent
 * @param atEnd if true, look at the end of the file, otherwise look at the start
 * @returns offset which is safely after (or before) any incomplete spikes
 */
qint64 cutIncompleteAtStartOrEnd(SignalFile &file, float minlevel, bool atEnd);

/**
 * Cut spikes which are incomplete at the current position of a signal file.
 * @param file the signal file
 * @param minlevel level below which signal is considered silent
 * @param direction if 1, look forward, if -1, look backwards
 * @returns offset which is safely after (or before) any incomplete spikes
 */
qint64 cutIncompleteSpikes(SignalFile &file, float minlevel, int direction);

#endif // CUTINCOMPLETE_H
