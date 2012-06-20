#ifndef FILEMINMAXFINDER_H
#define FILEMINMAXFINDER_H

#include "progressthread.h"

class FileMinMaxFinder : public ProgressThread
{
    Q_OBJECT
public:
    explicit FileMinMaxFinder(QWidget *parent, const QString &filename);
    bool validResult;
    float min, max;

    static bool getMinMax(QWidget *parent, const QString &filename, float &min, float &max);

protected:
    void run();

private:
    QString filename;

    static QString lastFilename;
    static float lastMin, lastMax;
};

#endif // FILEMINMAXFINDER_H
