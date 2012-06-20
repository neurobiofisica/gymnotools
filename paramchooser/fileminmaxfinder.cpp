#include "fileminmaxfinder.h"
#include <QFile>

QString FileMinMaxFinder::lastFilename;
float FileMinMaxFinder::lastMin, FileMinMaxFinder::lastMax;

FileMinMaxFinder::FileMinMaxFinder(QWidget *parent, const QString &filename) :
    ProgressThread(parent)
{
    dlg->setWindowTitle("Reading file");
    this->filename = filename;
    validResult = false;
}

void FileMinMaxFinder::run()
{
    QFile file(filename);
    if(!file.open(QIODevice::ReadOnly))
        return;

    quint16 i = 0;
    float sample;
    if(file.read((char*)&sample, sizeof(sample)) != sizeof(sample))
        return;
    min = max = sample;

    emit progressRangeChanged(0, file.size());
    emit progressValueChanged(0);

    while(file.read((char*)&sample, sizeof(sample)) == sizeof(sample)) {
        if(sample < min)
            min = sample;
        if(sample > max)
            max = sample;
        if(i++ == 0) {
            emit progressValueChanged(file.pos());
            if(wasCanceled())
                return;
        }
    }

    file.close();
    validResult = true;
}

bool FileMinMaxFinder::getMinMax(QWidget *parent, const QString &filename, float &min, float &max)
{
    if(filename == lastFilename) {
        min = lastMin;
        max = lastMax;
        return true;
    }

    FileMinMaxFinder finder(parent, filename);
    finder.startWait();
    if(finder.validResult) {
        lastFilename = filename;
        lastMin = min = finder.min;
        lastMax = max = finder.max;
        return true;
    }

    return false;
}
