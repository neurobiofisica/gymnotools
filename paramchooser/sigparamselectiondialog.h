#ifndef SIGPARAMSELECTIONDIALOG_H
#define SIGPARAMSELECTIONDIALOG_H

#include <QDialog>
#include <QHBoxLayout>
#include <QSpinBox>
#include <QDoubleSpinBox>

#include "common/signalfile.h"

class QwtPlot;
class QwtPlotZoomer;
class QwtPlotPanner;
class QwtPlotCurve;
class QwtPlotMarker;

namespace Ui {
    class SigParamSelectionDialog;
}

class SigParamSelectionDialog : public QDialog
{
    Q_OBJECT

public:
    explicit SigParamSelectionDialog(const QString &filename, QWidget *parent = 0);
    ~SigParamSelectionDialog();

private:
    Ui::SigParamSelectionDialog *ui;

protected:
    virtual void posChanged() = 0;
    bool changePosWithoutCallingVirtual(qint64 pos);
    QwtPlot *plot;
    QwtPlotZoomer *zoomer;
    QwtPlotPanner *panner;
    QWidget *paramArea;
    QHBoxLayout *paramAreaLayout;
    SignalFile file;
    qint64 curPos;
    double *xdata;

protected slots:
    virtual void on_btnLeft_clicked();
    virtual void on_btnRight_clicked();
    void changePos(qint64 pos);

private slots:
    void on_btnGo_clicked();
    void on_btnWaveform_clicked();
};

class SigParamLowpassDialog : public SigParamSelectionDialog
{
    Q_OBJECT

public:
    explicit SigParamLowpassDialog(const QString &filename, int numtaps, float cutoff, QWidget *parent = 0);
    ~SigParamLowpassDialog();

    QSpinBox *sbTaps;
    QDoubleSpinBox *sbCutoff;

protected:
    virtual void posChanged();

private slots:
    void filtParamChanged();
    void channelChanged();

private:
    void replotData();
    double *filtData, *diffData;
    SignalBuffer *buffer;
    QSpinBox *sbChannel;
    QwtPlotCurve *filtCurve, *diffCurve;
    QwtPlotZoomer *zoomer2;
};

class SigParamDetectionDialog : public SigParamSelectionDialog
{
    Q_OBJECT

public:
    explicit SigParamDetectionDialog(const QString &filename, int numtaps, float cutoff, double threshold, QWidget *parent = 0);
    ~SigParamDetectionDialog();

    QDoubleSpinBox *sbThreshold;

protected:
    virtual void posChanged();

private slots:
    void replotData();

private:
    QwtPlotCurve *curve, *shadowCurve;
    QwtPlotMarker *thresholdMarker;
    double *ydata, *shadowData;
    SignalBuffer *buffer;
};

class SigParamWithDualThreshold : public SigParamSelectionDialog
{
    Q_OBJECT

public:
    explicit SigParamWithDualThreshold(const QString &filename, double thresholdL, double thresholdH, QWidget *parent = 0);
    ~SigParamWithDualThreshold();

protected:
    virtual void posChanged();

protected slots:
    void thresholdLChanged(double thresholdL);
    void thresholdHChanged(double thresholdH);
    void channelChanged(int ch);

private:
    void replotData();
    int curChannel;
    double curThresholdL, curThresholdH;
    QwtPlotCurve *curve, *shadowCurveL, *shadowCurveH;
    QwtPlotMarker *thresholdMarkerL, *thresholdMarkerH;
    float *readBuf;
    double *ydata, *shadowDataL, *shadowDataH;
};

class SigParamSVMDialog : public SigParamWithDualThreshold
{
    Q_OBJECT

public:
    explicit SigParamSVMDialog(const QString &filename, double threshold, QWidget *parent = 0);
    ~SigParamSVMDialog();

    QDoubleSpinBox *sbThreshold;

private:
    QSpinBox *sbChannel;

private slots:
    void thresholdChanged(double threshold);
};

class SigParamSaturationDialog : public SigParamWithDualThreshold
{
    Q_OBJECT

public:
    explicit SigParamSaturationDialog(const QString &filename, double thresholdL, double thresholdH,
                                      float min, float max, QWidget *parent = 0);
    ~SigParamSaturationDialog();

    QDoubleSpinBox *sbThresholdL;
    QDoubleSpinBox *sbThresholdH;

protected slots:
    virtual void on_btnLeft_clicked();
    virtual void on_btnRight_clicked();

private:
    void findNextSpot(int direction);
    float sigMin, sigMax;
    float *findBuf;
    QSpinBox *sbChannel;
};

#endif // SIGPARAMSELECTIONDIALOG_H
