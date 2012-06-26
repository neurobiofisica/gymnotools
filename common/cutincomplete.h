#ifndef CUTINCOMPLETE_H
#define CUTINCOMPLETE_H

#include "signalfile.h"

/**
 * Cut spikes which are incomplete at the start or at the end of a signal file.
 * @param file the signal file
 * @param atEnd if true, look at the end of the file, otherwise look at the start
 * @param minlevel level below which signal is considered silent
 * @returns offset which is safely after (or before) any incomplete spikes
 */
qint64 cutIncompleteSpikes(SignalFile &file, bool atEnd, float minlevel);

#endif // CUTINCOMPLETE_H
