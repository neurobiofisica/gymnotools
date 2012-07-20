#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <QList>
#include <QString>
#include <QStringList>

#include "common/commoninit.h"
#include "common/sigcfg.h"
#include "common/windowfile.h"
#include "common/resizablebuffer.h"

#define DSFMT_MEXP 19937
#include "dsfmt/dSFMT.h"
#include "dsfmt/entropy.h"

static void cmd_info(WindowFile &infile)
{
    qint64 off;
    qint64 numEvents = 0, numWins = 0;

    infile.nextEvent();
    off = infile.getEventOffset();
    puts(QString("first event:\n"
                 "  bytes:   %1\n"
                 "  samples: %2\n"
                 "  seconds: %3\n")
         .arg(off)
         .arg(off / BytesPerSample)
         .arg((off / BytesPerSample)/(double)SamplingRate, 0, 'f', 6)
         .toUtf8().data());

    do {
        numEvents++;
        numWins += infile.getEventChannels();
    } while(infile.nextEvent());

    off = infile.getEventOffset();
    puts(QString("last event:\n"
                 "  bytes:   %1\n"
                 "  samples: %2\n"
                 "  seconds: %3\n\n"
                 "number of:\n"
                 "  events: %4\n"
                 "  channel windows: %5\n")
         .arg(off)
         .arg(off / BytesPerSample)
         .arg((off / BytesPerSample)/(double)SamplingRate, 0, 'f', 6)
         .arg(numEvents)
         .arg(numWins)
         .toUtf8().data());
}

static void cmd_range(WindowFile &infile, qint64 start, qint64 end, WindowFile &outfile)
{
    ResizableBuffer buf;
    while(infile.nextEvent()) {
        const qint64 off = infile.getEventOffset();
        if(off > end)
            break;
        if(off >= start) {
            const qint32 samples = infile.getEventSamples();
            const qint32 channels = infile.getEventChannels();
            buf.reserve(samples);
            outfile.writeEvent(off, samples, channels);
            for(int ch = 0; ch < channels; ch++) {
                infile.nextChannel();
                infile.read((char*)buf.buf(), samples*sizeof(float));
                outfile.writeChannel(infile.getChannelId(), buf.buf());
            }
        }
    }
}

static int cmd_random(WindowFile &infile, QList<double> &probabilities,
                      QList<WindowFile*> &outfiles)
{
    ResizableBuffer buf;

    assert(probabilities.length() == outfiles.length());
    int len = probabilities.length();

    QList<double> accprobs;
    {
        double accprob = 0.;
        foreach(double probability, probabilities) {
            accprob += probability;
            accprobs.append(accprob);
        }

        if(accprob > 1.) {
            fprintf(stderr, "cmd_random: sum of probabilities must be less than one.\n");
            return 1;
        }
    }

    int *channelsInFile = new int[len];
    WindowFile *destFileForChannel[NumChannels];

    while(infile.nextEvent()) {
        const qint64 off = infile.getEventOffset();
        const qint32 samples = infile.getEventSamples();
        const qint32 channels = infile.getEventChannels();
        buf.reserve(samples);

        memset(channelsInFile, 0, len*sizeof(int));
        memset(destFileForChannel, 0, sizeof(destFileForChannel));

        for(int ch = 0; ch < channels; ch++) {
            const double rand = dsfmt_gv_genrand_close_open();
            int fileno = 0;
            foreach(const double accprob, accprobs) {
                if(rand < accprob) {
                    channelsInFile[fileno]++;
                    destFileForChannel[ch] = outfiles.at(fileno);
                    break;
                }
                ++fileno;
            }
        }

        int fileno = 0;
        foreach(WindowFile * const outfile, outfiles) {
            outfile->writeEvent(off, samples, channelsInFile[fileno]);
            ++fileno;
        }

        for(int ch = 0; ch < channels; ch++) {
            WindowFile * const outfile = destFileForChannel[ch];
            infile.nextChannel();
            if(destFileForChannel[ch] != 0) {
                infile.read((char*)buf.buf(), samples*sizeof(float));
                outfile->writeChannel(infile.getChannelId(), buf.buf());
            }
        }

    }

    delete [] channelsInFile;
    return 0;
}

static int usage(const char *progname)
{
    fprintf(stderr, "Usage:\n");
    fprintf(stderr, "%s info infile\n"
            "  Show information about infile.\n", progname);
    fprintf(stderr, "%s range infile start-end samples|bytes|seconds outfile\n"
            "  Slices infile from start to end (samples, bytes or seconds),\n"
            "  producing an outfile containing only that range.\n", progname);
    fprintf(stderr, "%s random infile [prob_1 outfile_1 [prob_2 outfile_2 [...]]\n"
            "  Slices infile randomly, outputing channels to outfile_i with\n"
            "  probability prob_i. Output files are guaranteed to be disjoint.\n",
            progname);
    return 1;
}

int main(int argc, char **argv) {
    commonInit();

    if(argc < 3)
        return usage(argv[0]);

    WindowFile infile(argv[2]);
    if(!infile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "can't open file '%s' for reading.\n", argv[2]);
        return 1;
    }

    if(!strcmp(argv[1], "info")) {
        if(argc != 3)
            return usage(argv[0]);
        cmd_info(infile);
    }
    else if(!strcmp(argv[1], "range")) {
        if(argc != 6)
            return usage(argv[0]);

        QStringList intervalArg = QString(argv[3]).split("-");
        if(intervalArg.length() != 2) {
            fprintf(stderr, "invalid start-end range\n\n");
            return usage(argv[0]);
        }

        bool oks = true, oke = true;
        qint64 istart = 0 , iend = 0;
        double fstart = 0., fend = 0.;

        if(!strcmp(argv[4], "seconds")) {
            fstart = intervalArg.at(0).toDouble(&oks);
            fend   = intervalArg.at(1).toDouble(&oke);
        }
        else {
            istart = intervalArg.at(0).toLongLong(&oks);
            iend   = intervalArg.at(1).toLongLong(&oke);
        }
        if(!oks || !oke) {
            fprintf(stderr, "invalid numbers in start-end range\n\n");
            return usage(argv[0]);
        }

        if(!strcmp(argv[4], "samples")) {
            istart *= BytesPerSample;
            iend *= BytesPerSample;
        }
        else if(!strcmp(argv[4], "seconds")) {
            istart = (qint64)(fstart * SamplingRate) * BytesPerSample;
            iend   = (qint64)(fend   * SamplingRate) * BytesPerSample;
        }
        else if(!strcmp(argv[4], "bytes")) {
            // needs no conversion
        }
        else {
            fprintf(stderr, "unknown '%s' unit\n\n", argv[4]);
            return usage(argv[0]);
        }

        WindowFile outfile(argv[5]);
        if(!outfile.open(QIODevice::WriteOnly)) {
            fprintf(stderr, "can't open file '%s' for writing.\n", argv[5]);
            return 1;
        }

        cmd_range(infile, istart, iend, outfile);
        outfile.close();
    }
    else if(!strcmp(argv[1], "random")) {
        if(argc < 3 || (argc % 2 != 1))
            return usage(argv[0]);

        dsfmt_gv_init_with_entropy();

        QList<double> probabilities;
        QList<WindowFile*> outfiles;

        for(int i = 3; i < argc; i += 2) {
            bool ok = true;
            double probability = QString(argv[i]).toDouble(&ok);
            if(!ok) {
                fprintf(stderr, "invalid probability '%s'.\n", argv[i]);
                return 1;
            }
            WindowFile *outfile = new WindowFile(argv[i+1]);
            if(!outfile->open(QIODevice::WriteOnly)) {
                fprintf(stderr, "can't open file '%s' for writing.\n", argv[i+1]);
                return 1;
            }
            probabilities.append(probability);
            outfiles.append(outfile);
        }

        if(cmd_random(infile, probabilities, outfiles))
            return 1;

        foreach(WindowFile *const outfile, outfiles) {
            outfile->close();
            delete outfile;
        }
    }
    else return usage(argv[0]);

    infile.close();
    return 0;
}
