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
    void readCh(SignalBuffer &buf);
    void setFilter(int numtaps, float cutoff);
    void readFilteredCh(SignalBuffer &buf);
private:
    ResizableBuffer internalBuffer;
    float *filter;
    int filterLen;
};

#endif // SIGNALFILE_H
