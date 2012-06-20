#ifndef VIEWORIGINALSIGNALDIALOG_H
#define VIEWORIGINALSIGNALDIALOG_H

#include <QDialog>

class QwtPlotCurve;
class QwtPlotZoomer;
class QwtPlotPanner;

namespace Ui {
    class ViewOriginalSignalDialog;
}

class ViewOriginalSignalDialog : public QDialog
{
    Q_OBJECT

public:
    explicit ViewOriginalSignalDialog(const QString &filename, qint64 curPos, int channel = 0, QWidget *parent = 0);
    ~ViewOriginalSignalDialog();

private slots:
    void on_spinChannel_valueChanged(int channel);

private:
    Ui::ViewOriginalSignalDialog *ui;
    QwtPlotCurve *curve;
    QwtPlotZoomer *zoomer;
    QwtPlotPanner *panner;
    double *xdata, *ydata;
    float *readBuf;
};

#endif // VIEWORIGINALSIGNALDIALOG_H
