#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <QApplication>
#include <QFile>
#include <QFileInfo>

#include "common/commoninit.h"
#include "windowviewdialog.h"

int main(int argc, char **argv)
{
    new QApplication(argc, argv);
    commonInit();

    if(argc != 2 && argc != 3) {
        fprintf(stderr, "usage: %s input.spikes [original.I32]\n", argv[0]);
        return 1;
    }

    QFile infile(argv[1]);
    if(!infile.open(QIODevice::ReadOnly)) {
        fprintf(stderr, "error: couldn't open the input file (%s).\n", argv[1]);
        return 1;
    }

    QString origFilename;
    if(argc == 3) {
        QFileInfo fileinfo(argv[2]);
        if(fileinfo.isReadable() && fileinfo.isFile()) {
            origFilename = argv[2];
        }
        else {
            fprintf(stderr, "error: couldn't read the original file (%s).\n", argv[2]);
            return 1;
        }
    }

    WindowViewDialog *dlg = new WindowViewDialog();
    dlg->exec();

    return 0;
}
