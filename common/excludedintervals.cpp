#include <stdio.h>
#include <QRegExp>
#include <QStringList>
#include <QtAlgorithms>
#include "excludedintervals.h"

void ExcludedIntervalList::parseFile(QFile &file)
{
    QRegExp rxLine("(\\d+)\\s*-\\s*(\\d+)\\s*:\\s*([0-9, ]+)\n?");
    QRegExp rxNum("(\\d+)");
    char line[1024];
    int lineno = 1;
    while(file.readLine(line, sizeof(line)) != -1) {
        // parse line using regex
        if(!rxLine.exactMatch(line)) {
            fprintf(stderr, "ExcludedIntervals: line %d: "
                    "malformed line\n", lineno++);
            continue;
        }
        // store start and end
        ExcludedInterval interval;
        interval.start = rxLine.cap(1).toLong() * BytesPerSample;
        interval.end   = rxLine.cap(2).toLong() * BytesPerSample;
        // sanity check [start, end]
        if(interval.end <= interval.start) {
            fprintf(stderr, "ExcludedIntervals: line %d: "
                    "interval ends before it starts\n",
                    lineno++);
            continue;
        }
        // initialize chExcluded
        for(int ch = 0; ch < NumChannels; ch++) {
            interval.chExcluded[ch] = false;
        }
        // parse the channel list
        foreach(const QString &str, rxLine.cap(3).split(",")) {
            if(rxNum.indexIn(str) == -1) {
                fprintf(stderr, "ExcludedIntervals: line %d: "
                        "malformed channel\n", lineno++);
                continue;
            }
            int ch = rxNum.cap(1).toInt();
            if(ch < 0 || ch >= NumChannels) {
                fprintf(stderr, "ExcludedIntervals: line %d: "
                        "channel %d outside range\n",
                        lineno++, ch);
                continue;
            }
            interval.chExcluded[ch] = true;
        }
        // append the interval
        append(interval);
        // increase line number
        lineno++;
    }
    // assert the container is sorted
    qSort(begin(), end());
    // check if intervals are disjoint
    ConstIterator it = begin();
    if(it != end()) {
        qint64 lastEnd = (*it).end;
        for(++it; it != end(); ++it) {
            if((*it).start <= lastEnd) {
                fprintf(stderr, "ExcludedIntervals: there are non-disjoint "
                        "intervals in the list.\n");
                break;
            }
        }
    }
}

void ExcludedIntervalList::writeFile(QFile &file)
{
    for(ConstIterator it = begin(); it != end(); ++it) {
        long start = (*it).start / BytesPerSample;
        long end = (*it).end / BytesPerSample;
        QStringList channels;
        for(int ch = 0; ch < NumChannels; ch++) {
            if((*it).chExcluded[ch]) {
                channels.append(QString("%1").arg(ch));
            }
        }
        file.write(QString("%1-%2: %3\n").arg(start).arg(end).arg(channels.join(",")).toUtf8());
    }
}
