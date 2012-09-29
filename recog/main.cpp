#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <assert.h>
#include <math.h>
#include <db.h>
#include <limits>

#include <QtAlgorithms>
#include <QString>
#include <QStringList>
#include <QTextStream>
#include <QList>
#include <QFile>
#include <QPair>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "common/sigcfg.h"
#include "common/signalbuffer.h"
#include "common/windowfile.h"
#include "common/compilerspecific.h"

static int recogdb_compare(DB *dbp, const DBT *a, const DBT *b)
{
    (void) dbp;
    qint64 ai, bi;
    memcpy(&ai, a->data, sizeof(ai));
    memcpy(&bi, b->data, sizeof(bi));
    if(ai < bi)
        return -1;
    else if(ai > bi)
        return 1;
    return 0;
}

// XXX Not very portable, doesn't deal correctly with alignment issues
// Record layout:
// { presentFish, distA, distB, distAB,
//   [{offA, sizeA, {Ach0, Ach1, ...}}],
//   [{offB, sizeB, {Bch0, Bch1, ...}}] }
class RecogDB
{
private:
    DB *dbp;
    DBC *curp;
    DBT key, data;
    float *recbuf;

    void copybuf(float *&recbuff, qint32 *&recbufi,
                 qint32 off, qint32 size, const float *const* data)
    {
        recbufi[0] = off;
        recbufi[1] = size;
        recbuff = &recbuff[2];
        recbufi = &recbufi[2];
        for(int ch = 0; ch < NumChannels; ch++) {
            memcpy(recbuff, data[ch], size*sizeof(float));
            recbuff = &recbuff[size];
            recbufi = &recbufi[size];
        }
    }

public:
    explicit RecogDB(const char *filename)
        :dbp(NULL), curp(NULL)
    {
        assert(sizeof(float) == sizeof(qint32));
        recbuf = new float[8 + 2*NumChannels*EODSamples];

        db_create(&dbp, NULL, 0);
        dbp->set_bt_compare(dbp, recogdb_compare);
        dbp->open(dbp, NULL, filename, NULL, DB_BTREE, DB_CREATE, 0);
        dbp->cursor(dbp, NULL, &curp, 0);

        memset(&key, 0, sizeof(key));
        memset(&data, 0, sizeof(data));
    }

    ~RecogDB()
    {
        delete[] recbuf;

        if(curp != NULL)
            curp->close(curp);
        if(dbp != NULL)
            dbp->close(dbp, 0);
    }

    int first() { return curp->get(curp, &key, &data, DB_FIRST); }
    int last()  { return curp->get(curp, &key, &data, DB_LAST);  }
    int next()  { return curp->get(curp, &key, &data, DB_NEXT);  }
    int prev()  { return curp->get(curp, &key, &data, DB_PREV);  }

    int search(qint64 k)
    {
        key.data = (void *)&k;
        key.size = sizeof(k);
        return curp->get(curp, &key, &data, DB_SET);
    }

    qint64 k() const { return *(const qint64 *)key.data; }

    qint32 presentFish() const {
        const qint32 *p = (const qint32 *)data.data;
        return p[0];
    }
    float distA() const {
        const float *p = (const float *)data.data;
        return p[1];
    }
    float distB() const {
        const float *p = (const float *)data.data;
        return p[2];
    }
    float distAB() const {
        const float *p = (const float *)data.data;
        return p[3];
    }
    qint32 spikeData(int n, qint32 &off, SignalBuffer &buf) const {
        assert(n==1 || n==2);
        assert(data.size > 6*sizeof(qint32));
        const qint32 *p = (const qint32 *)data.data;
        p = &p[4];
        if(n==2) {
            qint32 firstSize = p[1];
            assert(data.size > (8 + NumChannels*firstSize)*sizeof(qint32));
            p = &p[2 + NumChannels*firstSize];
        }
        off = p[0];
        qint32 size = p[1];
        assert(buf.spc() >= size);
        p = &p[2];
        for(int ch = 0; ch < NumChannels; ch++) {
            memcpy(buf.ch(ch), p, size*sizeof(float));
            p = &p[size];
        }
        return size;
    }

    void insert(qint64 k, float distA, float distB, float distAB,
                qint32 offA, qint32 sizeA, const float *const* dataA,
                qint32 offB, qint32 sizeB, const float *const *dataB)
    {
        qint32 presentFish = 0;
        if(dataA != NULL && sizeA)
            presentFish |= 1;
        if(dataB != NULL && sizeB)
            presentFish |= 2;

        float  *recbuff = (float *)recbuf;
        qint32 *recbufi = (qint32 *)recbuf;

        recbufi[0] = presentFish;
        recbuff[1] = distA;
        recbuff[2] = distB;
        recbuff[3] = distAB;

        recbuff = &recbuff[4];
        recbufi = &recbufi[4];

        if(dataA != NULL && sizeA)
            copybuf(recbuff, recbufi, offA, sizeA, dataA);
        if(dataB != NULL && sizeB)
            copybuf(recbuff, recbufi, offB, sizeB, dataB);

        DBT recdata;
        memset(&recdata, 0, sizeof(recdata));
        recdata.data = (void *)recbuf;
        recdata.size = (recbuff-recbuf)*sizeof(recbuf[0]);

        key.data = (void *)&k;
        key.size = sizeof(k);

        dbp->put(dbp, NULL, &key, &recdata, DB_OVERWRITE_DUP);
    }
};

typedef QPair<qint64,qint64> SFishPair;

static QList<SFishPair> parseSFish(QFile &sfishfile)
{
    QTextStream s(&sfishfile);
    QList<SFishPair> list;
    while(true) {
        qint64 fishAoff, fishBoff;
        s >> fishAoff >> fishBoff;
        if(!s.atEnd())
            list.append(SFishPair(fishAoff, fishBoff));
        else break;
    }
    return list;
}

static AINLINE bool saturate(afloat *signal, int len,
                             float saturationLow, float saturationHigh)
{
    bool saturated = false;
    for(int i = 0; i < len; i++) {
        if(signal[i] > saturationHigh) {
            signal[i] = saturationHigh;
            saturated = true;
        }
        if(signal[i] < saturationLow) {
            signal[i] = saturationLow;
            saturated = true;
        }
    }
    return saturated;
}

static AINLINE float sqr(float x) {
    return x*x;
}

static const float inf = std::numeric_limits<float>::infinity();
static const int WinWorkerBufLen = 512*EODSamples;

class WinWorker
{
private:
    RecogDB &db;
    WindowFile &winfile;
    float saturationLow, saturationHigh;
    afloat **fishvecA, **fishvecB;

    static int instances;

    static qint32 fishlenA, fishlenB;
    static float fishA[NumChannels][EODSamples] ALIGN(16);
    static float fishB[NumChannels][EODSamples] ALIGN(16);
    static float buf[NumChannels][WinWorkerBufLen] ALIGN(16);

public:
    WinWorker(RecogDB &db, WindowFile &winfile,
              float saturationLow, float saturationHigh)
        : db(db),
          winfile(winfile),
          saturationLow(saturationLow),
          saturationHigh(saturationHigh)
    {
        assert("singleton" && (instances++) == 0);

        fishvecA = new afloat*[NumChannels];
        fishvecB = new afloat*[NumChannels];
        for(int ch = 0; ch < NumChannels; ch++) {
            fishvecA[ch] = &fishA[ch][0];
            fishvecB[ch] = &fishB[ch][0];
        }
    }
    ~WinWorker()
    {
        delete[] fishvecA;
        delete[] fishvecB;
    }

    void emitSingleA()
    {
        // copy spike
        fishlenA = winfile.getEventSamples();
        for(int ch = 0; ch < NumChannels; ch++) {
            winfile.nextChannel();
            winfile.read((char*)fishvecA[ch], fishlenA*sizeof(float));
            saturate(fishvecA[ch], fishlenA, saturationLow, saturationHigh);
        }
        // emit to db
        db.insert(winfile.getEventOffset(), 0., inf, inf,
                  0, fishlenA, fishvecA,
                  0, 0, NULL);
    }
    void emitSingleB()
    {
        // copy spike
        fishlenB = winfile.getEventSamples();
        for(int ch = 0; ch < NumChannels; ch++) {
            winfile.nextChannel();
            winfile.read((char*)fishvecB[ch], fishlenB*sizeof(float));
            saturate(fishvecB[ch], fishlenB, saturationLow, saturationHigh);
        }
        // emit to db
        db.insert(winfile.getEventOffset(), 0., inf, inf,
                  0, 0, NULL,
                  0, fishlenB, fishvecB);
    }

    void recog()
    {
        const int len = winfile.getEventSamples();
        const int zfilling = qMax(fishlenA, fishlenB);
        assert(len + zfilling <= WinWorkerBufLen);
        const int firstpos = zfilling/2;

        // read window channels
        bool saturated = false;
        for(int ch = 0; ch < NumChannels; ch++) {
            afloat *data = &buf[ch][0];
            // insert zero filling
            memset(&data[0], 0, firstpos*sizeof(float));
            memset(&data[firstpos + len], 0, (zfilling - firstpos)*sizeof(float));
            // read channel
            winfile.nextChannel();
            winfile.read((char*)&data[firstpos], len*sizeof(float));
            // check if saturated and sanitize saturation
            saturated = saturate(data, len, saturationLow, saturationHigh) || saturated;
        }


        float distA = inf, distB = inf;
#pragma omp parallel sections
        {
#pragma omp section
            {
                // look the minimum distance for placing a single A fish
                const int firstposA = firstpos - fishlenA/2;
                const int lastposA  = firstposA + len;
                for(int fishposA = firstposA; fishposA < lastposA; fishposA++) {
                    float newdist = 0.;
                    for(int ch = 0; ch < NumChannels; ch++) {
                        const afloat *data = &buf[ch][0];
                        const afloat *fishdata = &fishA[ch][0];
                        for(int i = 0; i < fishposA; i++)
                            newdist += sqr(data[i]);
                        for(int i = fishposA, j = 0; j < fishlenA; i++, j++)
                            newdist += sqr(data[i] - fishdata[j]);
                        for(int i = fishposA + fishlenA; i < firstpos + len; i++)
                            newdist += sqr(data[i]);
                    }
                    distA = qMin(distA, newdist);
                }
            }

#pragma omp section
            {
                // just like the above, but for a single B fish (manually unrolled)
                const int firstposB = firstpos - fishlenB/2;
                const int lastposB  = firstposB + len;
                for(int fishposB = firstposB; fishposB < lastposB; fishposB++) {
                    float newdist = 0.;
                    for(int ch = 0; ch < NumChannels; ch++) {
                        const afloat *data = &buf[ch][0];
                        const afloat *fishdata = &fishB[ch][0];
                        for(int i = 0; i < fishposB; i++)
                            newdist += sqr(data[i]);
                        for(int i = fishposB, j = 0; j < fishlenB; i++, j++)
                            newdist += sqr(data[i] - fishdata[j]);
                        for(int i = fishposB + fishlenB; i < firstpos + len; i++)
                            newdist += sqr(data[i]);
                    }
                    distB = qMin(distB, newdist);
                }
            }
        }

        printf("recog: %30.5f %30.5f\n", distA, distB);
    }
};

int WinWorker::instances = 0;
qint32 WinWorker::fishlenA, WinWorker::fishlenB;
float WinWorker::fishA[NumChannels][EODSamples] ALIGN(16);
float WinWorker::fishB[NumChannels][EODSamples] ALIGN(16);
float WinWorker::buf[NumChannels][WinWorkerBufLen] ALIGN(16);

static void iterate(RecogDB &db, WindowFile &winfile, QList<SFishPair> &sfishlist,
                    float saturationLow, float saturationHigh, int direction)
{
    QListIterator<SFishPair> it(sfishlist);
    WinWorker worker(db, winfile, saturationLow, saturationHigh);
    bool foundFirst = false;

    // manually "optimized" scan for each direction
    if(direction < 0) {
        // go to the end of the window file
        while(winfile.nextEvent());

        // set up list iterators
        it.toBack();
        assert(it.hasPrevious());
        SFishPair curpair = it.previous();
        qint64 lookFor = qMax(curpair.first, curpair.second);

        // scan backwards over window file
        do {
            const qint64 off = winfile.getEventOffset();
            assert(winfile.getEventChannels() == NumChannels);
            if(off == lookFor) {
                foundFirst = true;
                if(off == curpair.first) {
                    worker.emitSingleA();
                    bool hasPrevious = winfile.prevEvent();
                    assert(hasPrevious);
                    assert(winfile.getEventOffset() == curpair.second);
                    worker.emitSingleB();
                }
                else {
                    worker.emitSingleB();
                    bool hasPrevious = winfile.prevEvent();
                    assert(hasPrevious);
                    assert(winfile.getEventOffset() == curpair.first);
                    worker.emitSingleA();
                }
                if(it.hasPrevious())
                    curpair = it.previous();
                else
                    curpair = SFishPair(-1, -1);
                lookFor = qMax(curpair.first, curpair.second);
            }
            else if(foundFirst) {
                worker.recog();
            }
        } while(winfile.prevEvent());
    }
    else {
        // set up list iterators
        it.toFront();
        assert(it.hasNext());
        SFishPair curpair = it.next();
        qint64 lookFor = qMin(curpair.first, curpair.second);

        // scan forward over window file
        while(winfile.nextEvent()) {
            const qint64 off = winfile.getEventOffset();
            assert(winfile.getEventChannels() == NumChannels);
            if(off == lookFor) {
                foundFirst = true;
                if(off == curpair.first) {
                    worker.emitSingleA();
                    bool hasNext = winfile.nextEvent();
                    assert(hasNext);
                    assert(winfile.getEventOffset() == curpair.second);
                    worker.emitSingleB();
                }
                else {
                    worker.emitSingleB();
                    bool hasNext = winfile.nextEvent();
                    assert(hasNext);
                    assert(winfile.getEventOffset() == curpair.first);
                    worker.emitSingleA();
                }
                if(it.hasNext())
                    curpair = it.next();
                else
                    curpair = SFishPair(-1, -1);
                lookFor = qMin(curpair.first, curpair.second);
            }
            else if(foundFirst) {
                worker.recog();
            }
        }
    }
}

static void waveformAdjust(SignalBuffer &buf, WindowFile &outfile,
                           qint64 off, qint32 len,
                           float saturationLow, float saturationHigh,
                           float onlyabove, int fillsamples)
{
    static float adjbuf[NumChannels][EODSamples] ALIGN(16);

    // adjust spike in adjbuf
    const int firstpos = (EODSamples - len)/2;
    const int lastpos  = EODSamples - firstpos - 1;
    for(int ch = 0; ch < NumChannels; ch++) {
        const float *data = buf.ch(ch);
        float beginMean = 0., endMean = 0.;
        for(int i = 0; i < fillsamples && i < len; i++)
            beginMean += data[i];
        for(int i = len - 1; i >= len - fillsamples && i >= 0; i--)
            endMean += data[i];
        beginMean /= fillsamples;
        endMean /= fillsamples;
        for(int i = 0; i < firstpos; i++)
            adjbuf[ch][i] = beginMean;
        for(int i = lastpos; i < EODSamples; i++)
            adjbuf[ch][i] = endMean;
        memcpy(&adjbuf[ch][firstpos], data, len*sizeof(float));
    }

    // check which channels will be saved in outfile
    qint32 numSavedCh = 0;
    bool savedCh[NumChannels];
    for(int ch = 0; ch < NumChannels; ch++) {
        savedCh[ch] = false;
        const float *data = buf.ch(ch);
        bool chOk = false;
        for(int i = 0; i < EODSamples; i++) {
            const float sample = data[i];
            if(!chOk && fabsf(sample) >= onlyabove)
                chOk = true;
            if(sample <= saturationLow || sample >= saturationHigh) {
                chOk = false;
                break;
            }
        }
        if(chOk) {
            savedCh[ch] = true;
            numSavedCh++;
        }
    }

    // save
    outfile.writeEvent(off, EODSamples, numSavedCh);
    for(int ch = 0; ch < NumChannels; ch++) {
        if(savedCh[ch])
            outfile.writeChannel(ch, &adjbuf[ch][0]);
    }
}

static void waveform(RecogDB &db, WindowFile &fishAfile, WindowFile &fishBfile,
                     float saturationLow, float saturationHigh,
                     float onlyabove, int fillsamples)
{
    SignalBuffer buf(EODSamples);
    assert(db.first() == 0);
    do {
        const qint64 off = db.k();
        const qint32 fish = db.presentFish();
        qint32 displacement;
        if(fish == 1 || fish == 2) {
            const qint32 len = db.spikeData(1, displacement, buf);
            waveformAdjust(buf, fish == 1 ? fishAfile : fishBfile,
                           off + displacement*BytesPerSample, len,
                           saturationLow, saturationHigh,
                           onlyabove, fillsamples);
        }
        else {
            qint32 len = db.spikeData(1, displacement, buf);
            waveformAdjust(buf, fishAfile,
                           off + displacement*BytesPerSample, len,
                           saturationLow, saturationHigh,
                           onlyabove, fillsamples);
            len = db.spikeData(2, displacement, buf);
            waveformAdjust(buf, fishBfile,
                           off + displacement*BytesPerSample, len,
                           saturationLow, saturationHigh,
                           onlyabove, fillsamples);
        }
    } while(db.next() == 0);
}

static void txtexport(RecogDB &db, QFile &outfile, float isiwindow, float distfactor)
{
    // XXX stub
    (void) db;
    (void) outfile;
    (void) isiwindow;
    (void) distfactor;
}

static int usage(const char *progname)
{
    fprintf(stderr, "%s iterate [options] recog.db in.spikes in.singlefish\n", progname);
    fprintf(stderr, "options:\n"
            "  -z|--saturation=a,b Low and high saturation levels\n"
            "  -d|--direction=d    Scan direction (positive or negative)\n\n");

    fprintf(stderr, "%s waveform [options] recog.db outA.spikes outB.spikes\n", progname);
    fprintf(stderr, "options:\n"
            "  -z|--saturation=a,b Low and high saturation levels to filter out\n"
            "  -a|--onlyabove=a    Only output spikes above this amplitude\n"
            "  -f|--fillsamples=f  Number of samples used to compute filling amplitude\n\n");

    fprintf(stderr, "%s export [options] recog.db out.txt\n", progname);
    fprintf(stderr, "options:\n"
            "  -i|--isiwindow=i    Misdetection window around twice and half the last ISI\n"
            "  -d|--distfactor=d   Maximum distance factor to fix ISI misdetection\n\n");

    return 1;
}

int main(int argc, char **argv)
{
    const char *progname = argv[0];
    commonInit();
    if(argc < 2)
        return usage(progname);

    if(!strcmp(argv[1], "iterate")) {
        argc--;
        argv = &argv[1];

        float saturationLow = defaultSaturationLow;
        float saturationHigh = defaultSaturationHigh;
        int direction = 1;

        while(1) {
            int option_index = 0;
            static struct option long_options[] = {
                { "saturation", required_argument, 0, 'z' },
                { "direction",  required_argument, 0, 'd' },
                { 0, 0, 0, 0 }
            };

            int c = getopt_long(argc, argv, "z:d:", long_options, &option_index);
            if(c == -1)
                break;

            switch(c) {
            case 'z':
            {
                QStringList sl = QString(optarg).split(",");
                assert(sl.count() == 2);
                saturationLow = sl.at(0).toFloat();
                saturationHigh = sl.at(1).toFloat();
                break;
            }
            case 'd':
                direction = QString(optarg).toInt() >= 0 ? 1 : -1;
                break;
            default:
                return usage(progname);
            }
        }

        if(argc - optind != 3)
            return usage(progname);

        RecogDB db(argv[optind]);
        WindowFile winfile(argv[optind+1]);
        if(!winfile.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "Can't open window file (%s).\n", argv[optind+1]);
            return 1;
        }

        QFile sfishfile(argv[optind+2]);
        if(!sfishfile.open(QIODevice::ReadOnly)) {
            fprintf(stderr, "Can't open single fish file (%s).\n", argv[optind+2]);
            return 1;
        }
        QList<SFishPair> sfishlist = parseSFish(sfishfile);
        sfishfile.close();

        iterate(db, winfile, sfishlist, saturationLow, saturationHigh, direction);
        winfile.close();
    }
    else if(!strcmp(argv[1], "waveform")) {
        argc--;
        argv = &argv[1];

        float saturationLow = defaultSaturationLow;
        float saturationHigh = defaultSaturationHigh;
        float onlyabove = defaultOnlyAbove;
        int fillsamples = defaultRecogFillSamples;

        while(1) {
            int option_index = 0;
            static struct option long_options[] = {
                { "saturation",  required_argument, 0, 'z' },
                { "onlyabove",   required_argument, 0, 'a' },
                { "fillsamples", required_argument, 0, 'f' },
                { 0, 0, 0, 0 }
            };

            int c = getopt_long(argc, argv, "z:a:f:", long_options, &option_index);
            if(c == -1)
                break;

            switch(c) {
            case 'z':
            {
                QStringList sl = QString(optarg).split(",");
                assert(sl.count() == 2);
                saturationLow = sl.at(0).toFloat();
                saturationHigh = sl.at(1).toFloat();
                break;
            }
            case 'a':
                onlyabove = QString(optarg).toFloat();
                break;
            case 'f':
                fillsamples = QString(optarg).toInt();
                break;
            default:
                return usage(progname);
            }
        }

        if(argc - optind != 3)
            return usage(progname);

        RecogDB db(argv[optind]);
        WindowFile fishAfile(argv[optind+1]);
        if(!fishAfile.open(QIODevice::WriteOnly)) {
            fprintf(stderr, "Can't open fish A window file (%s).\n", argv[optind+1]);
            return 1;
        }
        WindowFile fishBfile(argv[optind+2]);
        if(!fishBfile.open(QIODevice::WriteOnly)) {
            fprintf(stderr, "Can't open fish B window file (%s).\n", argv[optind+2]);
            return 1;
        }

        waveform(db, fishAfile, fishBfile,
                 saturationLow, saturationHigh,
                 onlyabove, fillsamples);

        fishAfile.close();
        fishBfile.close();
    }
    else if(!strcmp(argv[1], "export")) {
        argc--;
        argv = &argv[1];

        float isiwindow = defaultRecogISIWindow;
        float distfactor = defaultRecogDistFactor;

        while(1) {
            int option_index = 0;
            static struct option long_options[] = {
                { "isiwindow",  required_argument, 0, 'i' },
                { "distfactor", required_argument, 0, 'd' },
                { 0, 0, 0, 0 }
            };

            int c = getopt_long(argc, argv, "i:d:", long_options, &option_index);
            if(c == -1)
                break;

            switch(c) {
            case 'i':
                isiwindow = QString(optarg).toFloat();
                break;
            case 'd':
                distfactor = QString(optarg).toFloat();
                break;
            default:
                return usage(progname);
            }
        }

        if(argc - optind != 2)
            return usage(progname);

        RecogDB db(argv[optind]);
        QFile outfile(argv[optind+1]);
        if(!outfile.open(QIODevice::WriteOnly)) {
            fprintf(stderr, "Can't open output file (%s).\n", argv[optind+1]);
            return 1;
        }

        txtexport(db, outfile, isiwindow, distfactor);

        outfile.close();
    }
    else return usage(progname);

    return 0;
}
