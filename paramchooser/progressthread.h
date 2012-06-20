#ifndef PROGRESSTHREAD_H
#define PROGRESSTHREAD_H

#include <QThread>
#include <QProgressDialog>

class ProgressThread : public QThread
{
    Q_OBJECT
signals:
    void progressValueChanged(int progress);
    void progressRangeChanged(int min, int max);
protected:
    QProgressDialog *dlg;
public:
    explicit ProgressThread(QWidget *parent = 0) {
        dlg = new QProgressDialog(parent);
        dlg->setWindowModality(Qt::WindowModal);
        dlg->setAutoReset(false);
        QObject::connect(this, SIGNAL(progressValueChanged(int)), dlg, SLOT(setValue(int)), Qt::QueuedConnection);
        QObject::connect(this, SIGNAL(progressRangeChanged(int,int)), dlg, SLOT(setRange(int,int)), Qt::QueuedConnection);
        QObject::connect(this, SIGNAL(finished()), dlg, SLOT(reset()));
    }
    ~ProgressThread() {
        delete dlg;
    }
    bool wasCanceled() const {
        return dlg->wasCanceled();
    }
    void startWait() {
        start();
        dlg->exec();
        wait();
    }
};

#endif // PROGRESSTHREAD_H
