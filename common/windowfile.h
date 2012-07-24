#ifndef WINDOWFILE_H
#define WINDOWFILE_H

#include <assert.h>
#include <QFile>

class WindowFile : public QFile
{
protected:
    qint64 curEventPos, curEventOffset;
    qint32 curEventLen, curEventSamples, curEventChannels,
           curChannelId, curChannel, lastEventLen;

    static const qint32 EventHdrLen = sizeof(lastEventLen) + sizeof(curEventOffset) +
            sizeof(curEventSamples) + sizeof(curEventChannels);

    /**
     * Reads an event from the current file position
     */
    void readEvent()
    {
        curEventPos = pos();
        read((char *)&lastEventLen, sizeof(lastEventLen));
        read((char *)&curEventOffset, sizeof(curEventOffset));
        read((char *)&curEventSamples, sizeof(curEventSamples));
        read((char *)&curEventChannels, sizeof(curEventChannels));
        curChannel = 0;
        curEventLen = EventHdrLen +
                curEventChannels*(sizeof(curChannelId) + curEventSamples*sizeof(float));
    }

public:
    WindowFile(const QString &name) :
        QFile(name),curEventPos(0),curEventLen(0),
        curEventChannels(0),curChannel(0) { }
    WindowFile(const QString &name, QObject *parent) :
        QFile(name,parent),curEventPos(0),curEventLen(0),
        curEventChannels(0),curChannel(0) { }

    qint64 getEventOffset() const { return curEventOffset; }
    qint32 getEventSamples() const { return curEventSamples; }
    qint32 getEventChannels() const { return curEventChannels; }
    qint32 getChannelId() const { return curChannelId; }

    /**
     * Rewinds the file so that it can be read like it was just opened.
     */
    void rewind()
    {
        seek(0);
        curEventPos = curEventLen = curEventChannels = curChannel = 0;
    }

    /**
     * Writes the occurrence of an event.
     * @param offset the offset at the original data file in which the event occurs
     * @param samples number of samples contained in payload channels
     * @param numchannels number of payload channels
     */
    void writeEvent(const qint64 &offset, const qint32 &samples, const qint32 &numchannels)
    {
        assert(curChannel == curEventChannels);
        lastEventLen = curEventLen;
        curEventLen = EventHdrLen +
                numchannels*(sizeof(curChannelId) + samples*sizeof(float));
        curEventOffset = offset;
        curEventSamples = samples;
        curEventChannels = numchannels;
        curChannel = 0;
        curEventPos = pos();
        write((const char *)&lastEventLen, sizeof(lastEventLen));
        write((const char *)&offset, sizeof(offset));
        write((const char *)&samples, sizeof(samples));
        write((const char *)&numchannels, sizeof(numchannels));
    }

    /**
     * Writes payload channel data associated with the current event.
     * Never call this function if outside an event.
     * @param channelid a number identifying the channel
     * @param data pointer to an array of floats with channel data
     */
    void writeChannel(const qint32 &channelid, const float *data)
    {
        assert(curChannel < curEventChannels);
        write((const char *)&channelid, sizeof(channelid));
        write((const char *)data, curEventSamples*sizeof(float));
        ++curChannel;
    }

    /**
     * Reads next event from the file
     * @returns true if successful
     */
    bool nextEvent()
    {
        const qint64 newPos = curEventPos + curEventLen;
        if((newPos >= size()) || !seek(newPos))
            return false;
        readEvent();
        curChannel = 0;
        return true;
    }

    /**
     * Reads previous event from the file
     * @returns true if successful
     */
    bool prevEvent()
    {
        const qint64 newPos = curEventPos - lastEventLen;
        if((curEventPos <= 0) || !seek(newPos))
            return false;
        readEvent();
        curChannel = 0;
        return true;
    }

    /**
     * Reads next channel from the file
     * @returns true if successful
     */
    bool nextChannel()
    {
        if(curChannel >= curEventChannels) {
            do {
                if(!nextEvent()) {
                    return false;
                }
            } while(curEventChannels == 0);
            curChannel = 0;
        }
        seek(curEventPos + EventHdrLen +
            curChannel*(sizeof(curChannelId) + curEventSamples*sizeof(float)));
        read((char *)&curChannelId, sizeof(curChannelId));
        ++curChannel;
        return true;
    }

    /**
     * Reads previous channel from the file
     * @returns true if successful
     */
    bool prevChannel()
    {
        if(curChannel <= 0) {
            do {
                if(!prevEvent()) {
                    return false;
                }
            } while(curEventChannels == 0);
            curChannel = curEventChannels;
        }
        --curChannel;
        seek(curEventPos + EventHdrLen +
            curChannel*(sizeof(curChannelId) + curEventSamples*sizeof(float)));
        read((char *)&curChannelId, sizeof(curChannelId));
        return true;
    }
};

#endif // WINDOWFILE_H
