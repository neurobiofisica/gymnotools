#ifndef WINDOWFILE_H
#define WINDOWFILE_H

#include <QFile>

class WindowFile : public QFile
{
protected:
    quint32 curEventLen;

public:
    WindowFile(const QString &name)
        :QFile(name),curEventLen(0) { }
    WindowFile(const QString &name, QObject *parent)
        :QFile(name, parent),curEventLen(0) { }

    /**
     * Writes the occurrence of an event. Never call writeChannel before calling this method.
     * @param offset the offset at the original data file in which the event occurs
     * @param samples number of samples contained in payload channels
     * @param numchannels number of payload channels
     */
    void writeEvent(const qint64 &offset, const qint32 &samples, const qint32 &numchannels)
    {
        curEventLen  = write((const char *)&curEventLen, sizeof(curEventLen));
        curEventLen += write((const char *)&offset, sizeof(offset));
        curEventLen += write((const char *)&samples, sizeof(samples));
        curEventLen += write((const char *)&numchannels, sizeof(numchannels));
    }

    /**
     * Writes payload channel data associated with the current event.
     * Never call this function if outside an event.
     * @param channelid a number identifying the channel
     * @param data pointer to an array of floats with channel data
     * @param samples number of samples contained in the array
     */
    void writeChannel(const qint32 &channelid, const float *data, const qint32 samples)
    {
        curEventLen += write((const char *)&channelid, sizeof(channelid));
        curEventLen += write((const char *)data, samples*sizeof(float));
    }

};

#endif // WINDOWFILE_H
