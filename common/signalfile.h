#ifndef SIGNALFILE_H
#define SIGNALFILE_H

#include <QFile>
#include "resizablebuffer.h"
#include "signalbuffer.h"

class SignalFile : public QFile
{
public:
    explicit SignalFile()                                     : QFile()            ,filter(NULL),filterLen(0) {}
    explicit SignalFile(const QString &name)                  : QFile(name)        ,filter(NULL),filterLen(0) {}
    explicit SignalFile(QObject *parent)                      : QFile(parent)      ,filter(NULL),filterLen(0) {}
    explicit SignalFile(const QString &name, QObject *parent) : QFile(name, parent),filter(NULL),filterLen(0) {}
    ~SignalFile();

    /**
     * Read channel data to a SignalBuffer
     * @param buf the SignalBuffer
     */
    void readCh(SignalBuffer &buf);

    /**
     * Set a lowpass filter to be used by readFilteredCh
     * @param numtaps number of taps
     * @param cutoff cut-off frequency
     */
    void setFilter(int numtaps, float cutoff);

    /**
     * Read lowpass-filtered channel data to a SignalBuffer
     * @param buf the SignalBuffer
     */
    void readFilteredCh(SignalBuffer &buf);
private:
    ResizableBuffer internalBuffer;
    float *filter;
    int filterLen;
};

#endif // SIGNALFILE_H
