#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>

#include <QApplication>
#include <QFile>
#include <QFileInfo>

#include "common/commoninit.h"
#include "common/windowfile.h"
#include "windowviewdialog.h"

static int usage(const char *progname)
{
    fprintf(stderr, "%s [options] windowfile [original.I32]\n",
            progname);
    fprintf(stderr, "options:\n"
            "  -w|--winatatime=w    Maximum number of windows to display at a time\n");
    return 1;
}

int main(int argc, char **argv)
{
    new QApplication(argc, argv);
    commonInit();

    int winatatime = 100;

    while(1) {
        int option_index = 0;
        static struct option long_options[] = {
            { "winatatime",  required_argument, 0, 'w' },
            { 0, 0, 0, 0 }
        };

        int c = getopt_long(argc, argv, "w:",
                            long_options, &option_index);
        if(c == -1)
            break;

        switch(c) {
        case 'w':
            winatatime = QString(optarg).toInt();
            break;
        default:
            return usage(argv[0]);
        }
    }

    if((argc - optind != 1) && (argc - optind != 2))
        return usage(argv[0]);

    WindowFile infile(argv[optind]);
    if(!infile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "error: couldn't open the input file (%s).\n", argv[optind]);
        return 1;
    }

    QString origFilename;
    if(argc - optind == 2) {
        QFileInfo fileinfo(argv[optind+1]);
        if(fileinfo.isReadable() && fileinfo.isFile()) {
            origFilename = argv[optind+1];
        }
        else {
            fprintf(stderr, "error: couldn't read the original file (%s).\n", argv[optind+1]);
            return 1;
        }
    }

    WindowViewDialog *dlg = new WindowViewDialog(infile, origFilename, winatatime);
    dlg->exec();

    return 0;
}
