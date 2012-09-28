#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <assert.h>
#include <math.h>
#include <db.h>
#include <limits>

#include <QString>
#include <QStringList>
#include <QFile>

#include "common/commoninit.h"
#include "common/defaultparams.h"
#include "common/sigcfg.h"
#include "common/signalbuffer.h"
#include "common/windowfile.h"

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
class RecogDB {
private:
    DB *dbp;
    DBC *curp;
    DBT key, data;
public:
    explicit RecogDB(const char *filename)
        :dbp(NULL), curp(NULL)
    {
        db_create(&dbp, NULL, 0);
        dbp->set_bt_compare(dbp, recogdb_compare);
        dbp->open(dbp, NULL, filename, NULL, DB_BTREE, DB_CREATE, 0);
        dbp->cursor(dbp, NULL, &curp, 0);
        memset(&key, 0, sizeof(key));
        memset(&data, 0, sizeof(data));
    }
    ~RecogDB()
    {
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
        return curp->get(curp, &key, &data, DB_SET);
    }

    qint64 k() const { return *(const qint64 *)key.data; }

    // Record layout:
    // { presentFish, distA, distB, distAB,
    //   [{offA, sizeA, {Ach0, Ach1, ...}}],
    //   [{offB, sizeB, {Bch0, Bch1, ...}}] }
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
        assert(sizeof(float) == sizeof(qint32));
        p = &p[2];
        for(int ch = 0; ch < NumChannels; ch++) {
            memcpy(buf.ch(ch), p, size*sizeof(float));
            p = &p[size];
        }
        return size;
    }


};

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
    commonInit();
    if(argc < 3)
        return usage(argv[0]);

    RecogDB db(argv[2]);

    if(!strcmp(argv[1], "iterate")) {

    }
    else if(!strcmp(argv[1], "waveform")) {

    }
    else if(!strcmp(argv[1], "export")) {

    }
    else return usage(argv[0]);

    return 0;
}
