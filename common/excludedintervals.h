#ifndef EXCLUDEDINTERVALS_H
#define EXCLUDEDINTERVALS_H

#include <QList>
#include <QFile>
#include "sigcfg.h"

/**
 * Struct which holds one excluded interval
 */
struct ExcludedInterval
{
    /**
     * Start offset in the file to exclude
     */
    qint64 start;
    /**
     * End offset in the file to exclude
     */
    qint64 end;
    /**
     * Channels in the interval which are excluded
     */
    bool chExcluded[NumChannels];
    /**
     * Comparison operator '<'. Another interval is considered
     * less than this one if it starts before this one.
     * @param other another interval
     */
    bool operator<(const struct ExcludedInterval &other) const
    {
        return start < other.start;
    }
};

/**
 * QList of ExcludedIntervals
 */
struct ExcludedIntervalList: public QList<ExcludedInterval>
{
    /**
     * Parses a QFile to fill up the list. The list is
     * guaranteed to be sorted after the parsing.
     * @param file the QFile
     */
    void parseFile(QFile &file);
    /**
     * Writes list contents to a file.
     * @param file on which to write
     */
    void writeFile(QFile &file);
};

#endif // EXCLUDEDINTERVALS_H
