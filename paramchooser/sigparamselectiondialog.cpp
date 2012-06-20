#include <QInputDialog>
#include <QLabel>

#include <qwt_plot_curve.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_panner.h>
#include <qwt_plot_marker.h>
#include <qwt_scale_engine.h>

#include "sigparamselectiondialog.h"
#include "ui_sigparamselectiondialog.h"

#include "commongui/vieworiginalsignaldialog.h"
#include "commongui/guicfg.h"
#include "commongui/guiutil.h"

static const int PassItems = PlotDialogNumPoints*NumChannels;
static const int PassBytes = PassItems*sizeof(float);

SigParamSelectionDialog::SigParamSelectionDialog(const QString &filename, QWidget *parent) :
    QDialog(parent),
    ui(new Ui::SigParamSelectionDialog)
{
    file.setFileName(filename);
    file.open(QFile::ReadOnly);
    curPos = 0;

    ui->setupUi(this);

    plot = ui->plot;
    plot->setCanvasBackground(QColor(Qt::black));
    plot->canvas()->setCursor(Qt::ArrowCursor);

    zoomer = new QwtPlotZoomer(QwtPlot::xBottom, QwtPlot::yLeft, plot->canvas());
    zoomer->setRubberBandPen(QColor(Qt::blue));
    zoomer->setTrackerPen(QColor(Qt::white));
    zoomer->setMousePattern(QwtEventPattern::MouseSelect2, Qt::RightButton, Qt::ControlModifier);
    zoomer->setMousePattern(QwtEventPattern::MouseSelect3, Qt::RightButton);

    panner = new QwtPlotPanner(plot->canvas());
    panner->setMouseButton(Qt::MidButton);

    paramArea = ui->paramArea;
    paramAreaLayout = ui->paramAreaLayout;

    xdata = new double[PlotDialogNumPoints];
}

SigParamSelectionDialog::~SigParamSelectionDialog()
{
    delete ui;
    delete [] xdata;
}

bool SigParamSelectionDialog::changePosWithoutCallingVirtual(qint64 pos)
{
    if(pos >= 0 && pos < file.size()) {
        curPos = pos;
        fillXData(xdata, pos);
        return true;
    }
    return false;
}

void SigParamSelectionDialog::changePos(qint64 pos)
{
    if(changePosWithoutCallingVirtual(pos))
        posChanged();
}

void SigParamSelectionDialog::on_btnGo_clicked()
{
    bool ok;
    double t = curPos/(double)BytesPerSample/(double)SamplingRate;
    t = QInputDialog::getDouble(this, "Go to", "Jump to time (in seconds):", t, 0, 2e9, 3, &ok);
    if(ok) {
        qint64 newPos = round(t*SamplingRate)*BytesPerSample;
        changePos(newPos);
    }
}

void SigParamSelectionDialog::on_btnWaveform_clicked()
{
    ViewOriginalSignalDialog dlg(file.fileName(), curPos, 0, this);
    dlg.exec();
}

void SigParamSelectionDialog::on_btnLeft_clicked()
{
    qint64 newPos = curPos - PassBytes;
    if(newPos < 0)
        newPos = 0;
    changePos(newPos);
}

void SigParamSelectionDialog::on_btnRight_clicked()
{
    qint64 newPos = curPos + PassBytes;
    changePos(newPos);
}

SigParamLowpassDialog::SigParamLowpassDialog(const QString &filename, int numtaps, float cutoff, QWidget *parent) :
    SigParamSelectionDialog(filename, parent)
{
    setWindowTitle("Derivative lowpass prefilter");

    paramAreaLayout->addWidget(new QLabel("Taps:", paramArea));
    sbTaps = new QSpinBox(paramArea);
    sbTaps->setRange(1, 101);
    sbTaps->setSingleStep(2);
    sbTaps->setValue(numtaps);
    paramAreaLayout->addWidget(sbTaps);

    paramAreaLayout->addWidget(new QLabel("Cutoff:", paramArea));
    sbCutoff = new QDoubleSpinBox(paramArea);
    sbCutoff->setRange(.01, 1.);
    sbCutoff->setSingleStep(.01);
    sbCutoff->setDecimals(2);
    sbCutoff->setValue(cutoff);
    paramAreaLayout->addWidget(sbCutoff);

    paramAreaLayout->addWidget(new QLabel("Channel:", paramArea));
    sbChannel = new QSpinBox(paramArea);
    sbChannel->setRange(0, NumChannels-1);
    sbChannel->setSingleStep(1);
    sbChannel->setValue(0);
    paramAreaLayout->addWidget(sbChannel);

    QObject::connect(sbTaps, SIGNAL(valueChanged(int)), this, SLOT(filtParamChanged()));
    QObject::connect(sbCutoff, SIGNAL(valueChanged(double)), this, SLOT(filtParamChanged()));
    QObject::connect(sbChannel, SIGNAL(valueChanged(int)), this, SLOT(channelChanged()));

    plot->enableAxis(QwtPlot::yRight);

    // use symmetric scales so that both curves share the zero baseline
    plot->axisScaleEngine(QwtPlot::yLeft)->setAttribute(QwtScaleEngine::Symmetric);
    plot->axisScaleEngine(QwtPlot::yRight)->setAttribute(QwtScaleEngine::Symmetric);

    filtCurve = new QwtPlotCurve();
    filtCurve->setRenderHint(QwtPlotItem::RenderAntialiased);
    filtCurve->setPen(QColor(Qt::green));
    filtCurve->setYAxis(QwtPlot::yLeft);
    filtCurve->attach(plot);

    diffCurve = new QwtPlotCurve();
    diffCurve->setRenderHint(QwtPlotItem::RenderAntialiased);
    diffCurve->setPen(QColor(Qt::red));
    diffCurve->setYAxis(QwtPlot::yRight);
    diffCurve->attach(plot);

    zoomer2 = new QwtPlotZoomer(QwtPlot::xTop, QwtPlot::yRight, plot->canvas());
    zoomer2->setTrackerMode(QwtPicker::AlwaysOff);
    zoomer2->setRubberBand(QwtPicker::NoRubberBand);
    zoomer2->setMousePattern(QwtEventPattern::MouseSelect2, Qt::RightButton, Qt::ControlModifier);
    zoomer2->setMousePattern(QwtEventPattern::MouseSelect3, Qt::RightButton);

    buffer = new SignalBuffer(PlotDialogNumPoints);
    filtData = new double[PlotDialogNumPoints];
    diffData = new double[PlotDialogNumPoints-1];
    file.setFilter(numtaps, cutoff);

    if(changePosWithoutCallingVirtual(0))
        SigParamLowpassDialog::posChanged();
}

SigParamLowpassDialog::~SigParamLowpassDialog()
{
    delete buffer;
    delete [] filtData;
    delete [] diffData;
}

void SigParamLowpassDialog::filtParamChanged()
{
    file.setFilter(sbTaps->value(), sbCutoff->value());
    replotData();
}

void SigParamLowpassDialog::channelChanged()
{
    posChanged();
}

void SigParamLowpassDialog::replotData()
{
    file.seek(curPos);
    file.readFilteredCh(*buffer);

    float *chbuf = buffer->ch(sbChannel->value());
    for(int i = 0; i < PlotDialogNumPoints; i++)
        filtData[i] = chbuf[i];
    buffer->diff();
    for(int i = 0; i < PlotDialogNumPoints - 1; i++)
        diffData[i] = chbuf[i];

    filtCurve->setRawSamples(xdata, filtData, PlotDialogNumPoints);
    diffCurve->setRawSamples(xdata, diffData, PlotDialogNumPoints-1);
    plot->replot();
}

void SigParamLowpassDialog::posChanged()
{
    // set autoscale back (may have been unset by zoomer)
    plot->setAxisAutoScale(QwtPlot::xBottom);
    plot->setAxisAutoScale(QwtPlot::yLeft);
    plot->setAxisAutoScale(QwtPlot::yRight);

    replotData();
    zoomer->setZoomBase();
    zoomer2->setZoomBase();
}

SigParamDetectionDialog::SigParamDetectionDialog(const QString &filename, int numtaps, float cutoff, double threshold, QWidget *parent) :
    SigParamSelectionDialog(filename, parent)
{
    setWindowTitle("Detection threshold");

    paramAreaLayout->addWidget(new QLabel("Threshold:", paramArea));
    sbThreshold = new QDoubleSpinBox(paramArea);
    sbThreshold->setRange(0., MaxAmplitude);
    sbThreshold->setSingleStep(.001);
    sbThreshold->setDecimals(4);
    sbThreshold->setValue(threshold);
    paramAreaLayout->addWidget(sbThreshold);

    QObject::connect(sbThreshold, SIGNAL(valueChanged(double)), this, SLOT(replotData()));

    curve = new QwtPlotCurve();
    curve->setRenderHint(QwtPlotItem::RenderAntialiased);
    curve->setPen(QColor(Qt::green));
    curve->attach(plot);

    shadowCurve = new QwtPlotCurve();
    shadowCurve->setRenderHint(QwtPlotItem::RenderAntialiased);
    shadowCurve->setPen(QColor(Qt::magenta));
    shadowCurve->setBrush(QColor(Qt::magenta));
    shadowCurve->setBaseline(threshold);
    shadowCurve->attach(plot);

    thresholdMarker = new QwtPlotMarker();
    thresholdMarker->setValue(0., threshold);
    thresholdMarker->setLineStyle(QwtPlotMarker::HLine);
    thresholdMarker->setLinePen(QPen(Qt::red, 0, Qt::DashLine));
    thresholdMarker->attach(plot);

    buffer = new SignalBuffer(PlotDialogNumPoints);
    ydata = new double[PlotDialogNumPoints - 1];
    shadowData = new double[PlotDialogNumPoints - 1];
    file.setFilter(numtaps, cutoff);

    if(changePosWithoutCallingVirtual(0))
        SigParamDetectionDialog::posChanged();
}

SigParamDetectionDialog::~SigParamDetectionDialog()
{
    delete buffer;
    delete [] ydata;
    delete [] shadowData;
}

void SigParamDetectionDialog::posChanged()
{
    // set autoscale back (may have been unset by zoomer)
    plot->setAxisAutoScale(QwtPlot::xBottom);
    plot->setAxisAutoScale(QwtPlot::yLeft);

    replotData();
    zoomer->setZoomBase();
}

void SigParamDetectionDialog::replotData()
{
    file.seek(curPos);
    file.readFilteredCh(*buffer);
    buffer->diff();

    float *squareSum = buffer->ch(0);
    buffer->sumSquares(squareSum);

    double threshold = sbThreshold->value();

    for(int i = 0; i < PlotDialogNumPoints - 1; i++) {
        const double sample = squareSum[i];
        ydata[i] = sample;
        shadowData[i] = (sample >= threshold) ? sample : threshold;
    }

    curve->setRawSamples(xdata, ydata, PlotDialogNumPoints - 1);
    shadowCurve->setRawSamples(xdata, shadowData, PlotDialogNumPoints - 1);
    shadowCurve->setBaseline(threshold);
    thresholdMarker->setValue(0., threshold);

    plot->replot();
}

SigParamWithDualThreshold::SigParamWithDualThreshold(const QString &filename, double thresholdL, double thresholdH, QWidget *parent) :
    SigParamSelectionDialog(filename, parent)
{
    curChannel = 0;
    curThresholdL = thresholdL;
    curThresholdH = thresholdH;

    curve = new QwtPlotCurve();
    curve->setRenderHint(QwtPlotItem::RenderAntialiased);
    curve->setPen(QColor(Qt::green));
    curve->attach(plot);

    shadowCurveL = new QwtPlotCurve();
    shadowCurveL->setRenderHint(QwtPlotItem::RenderAntialiased);
    shadowCurveL->setPen(QColor(Qt::magenta));
    shadowCurveL->setBrush(QColor(Qt::magenta));
    shadowCurveL->setBaseline(thresholdL);
    shadowCurveL->attach(plot);

    shadowCurveH = new QwtPlotCurve();
    shadowCurveH->setRenderHint(QwtPlotItem::RenderAntialiased);
    shadowCurveH->setPen(QColor(Qt::magenta));
    shadowCurveH->setBrush(QColor(Qt::magenta));
    shadowCurveH->setBaseline(thresholdH);
    shadowCurveH->attach(plot);

    thresholdMarkerL = new QwtPlotMarker();
    thresholdMarkerL->setValue(0., thresholdL);
    thresholdMarkerL->setLineStyle(QwtPlotMarker::HLine);
    thresholdMarkerL->setLinePen(QPen(Qt::red, 0, Qt::DashLine));
    thresholdMarkerL->attach(plot);

    thresholdMarkerH = new QwtPlotMarker();
    thresholdMarkerH->setValue(0., thresholdH);
    thresholdMarkerH->setLineStyle(QwtPlotMarker::HLine);
    thresholdMarkerH->setLinePen(QPen(Qt::red, 0, Qt::DashLine));
    thresholdMarkerH->attach(plot);

    readBuf = new float[PassItems];
    ydata = new double[PlotDialogNumPoints];
    shadowDataL = new double[PlotDialogNumPoints];
    shadowDataH = new double[PlotDialogNumPoints];

    if(changePosWithoutCallingVirtual(0))
        SigParamWithDualThreshold::posChanged();
}

SigParamWithDualThreshold::~SigParamWithDualThreshold()
{
    delete [] readBuf;
    delete [] ydata;
    delete [] shadowDataL;
    delete [] shadowDataH;
}

void SigParamWithDualThreshold::posChanged()
{
    // set autoscale back (may have been unset by zoomer)
    plot->setAxisAutoScale(QwtPlot::xBottom);
    plot->setAxisAutoScale(QwtPlot::yLeft);

    file.seek(curPos);
    memset(readBuf, 0, PassBytes);
    file.read((char*)readBuf, PassBytes);

    replotData();
    zoomer->setZoomBase();
}

void SigParamWithDualThreshold::channelChanged(int ch)
{
    curChannel = ch;
    posChanged();
}

void SigParamWithDualThreshold::thresholdHChanged(double thresholdH)
{
    curThresholdH = thresholdH;
    replotData();
}

void SigParamWithDualThreshold::thresholdLChanged(double thresholdL)
{
    curThresholdL = thresholdL;
    replotData();
}

void SigParamWithDualThreshold::replotData()
{
    for(int i = curChannel, j = 0; i < PassItems; i += NumChannels, j++) {
        const float sample = readBuf[i];
        ydata[j] = sample;
        shadowDataH[j] = (sample >= curThresholdH) ? sample : curThresholdH;
        shadowDataL[j] = (sample <= curThresholdL) ? sample : curThresholdL;
    }

    curve->setRawSamples(xdata, ydata, PlotDialogNumPoints);

    shadowCurveH->setRawSamples(xdata, shadowDataH, PlotDialogNumPoints);
    shadowCurveH->setBaseline(curThresholdH);
    thresholdMarkerH->setValue(0., curThresholdH);

    shadowCurveL->setRawSamples(xdata, shadowDataL, PlotDialogNumPoints);
    shadowCurveL->setBaseline(curThresholdL);
    thresholdMarkerL->setValue(0., curThresholdL);

    plot->replot();
}

SigParamSVMDialog::SigParamSVMDialog(const QString &filename, double threshold, QWidget *parent) :
    SigParamWithDualThreshold(filename, -threshold, threshold, parent)
{
    setWindowTitle("SVM usage threshold");

    paramAreaLayout->addWidget(new QLabel("Threshold:", paramArea));
    sbThreshold = new QDoubleSpinBox(paramArea);
    sbThreshold->setRange(0., MaxAmplitude);
    sbThreshold->setSingleStep(.01);
    sbThreshold->setDecimals(2);
    sbThreshold->setValue(threshold);
    paramAreaLayout->addWidget(sbThreshold);

    paramAreaLayout->addWidget(new QLabel("Channel:", paramArea));
    sbChannel = new QSpinBox(paramArea);
    sbChannel->setRange(0, NumChannels-1);
    sbChannel->setSingleStep(1);
    sbChannel->setValue(0);
    paramAreaLayout->addWidget(sbChannel);

    QObject::connect(sbThreshold, SIGNAL(valueChanged(double)), this, SLOT(thresholdChanged(double)));
    QObject::connect(sbChannel, SIGNAL(valueChanged(int)), this, SLOT(channelChanged(int)));
}

SigParamSVMDialog::~SigParamSVMDialog()
{
}

void SigParamSVMDialog::thresholdChanged(double threshold)
{
    thresholdHChanged( threshold);
    thresholdLChanged(-threshold);
}

SigParamSaturationDialog::SigParamSaturationDialog(const QString &filename, double thresholdL, double thresholdH,
                                                   float min, float max, QWidget *parent) :
    SigParamWithDualThreshold(filename, thresholdL, thresholdH, parent)
{
    setWindowTitle("Saturation threshold");

    paramAreaLayout->addWidget(new QLabel("Low threshold:", paramArea));
    sbThresholdL = new QDoubleSpinBox(paramArea);
    sbThresholdL->setRange(-MaxAmplitude, 0.);
    sbThresholdL->setSingleStep(.01);
    sbThresholdL->setDecimals(2);
    sbThresholdL->setValue(thresholdL);
    paramAreaLayout->addWidget(sbThresholdL);

    paramAreaLayout->addWidget(new QLabel("High threshold:", paramArea));
    sbThresholdH = new QDoubleSpinBox(paramArea);
    sbThresholdH->setRange(0., MaxAmplitude);
    sbThresholdH->setSingleStep(.01);
    sbThresholdH->setDecimals(2);
    sbThresholdH->setValue(thresholdH);
    paramAreaLayout->addWidget(sbThresholdH);

    paramAreaLayout->addWidget(new QLabel("Channel:", paramArea));
    sbChannel = new QSpinBox(paramArea);
    sbChannel->setRange(0, NumChannels-1);
    sbChannel->setSingleStep(1);
    sbChannel->setValue(0);
    paramAreaLayout->addWidget(sbChannel);

    QObject::connect(sbThresholdL, SIGNAL(valueChanged(double)), this, SLOT(thresholdLChanged(double)));
    QObject::connect(sbThresholdH, SIGNAL(valueChanged(double)), this, SLOT(thresholdHChanged(double)));
    QObject::connect(sbChannel, SIGNAL(valueChanged(int)), this, SLOT(channelChanged(int)));

    findBuf = new float[PassItems];

    sigMin = min;
    sigMax = max;
}

SigParamSaturationDialog::~SigParamSaturationDialog()
{
    delete [] findBuf;
}

void SigParamSaturationDialog::findNextSpot(int direction)
{
    qint64 pos = curPos;
    qint64 fileSize = file.size();
    while(1) {
        pos += direction*PassBytes;
        if(pos < 0 || pos >= fileSize)
            break;
        file.seek(pos);

        memset(findBuf, 0, PassBytes);
        file.read((char*)findBuf, PassBytes);

        for(int i = 0; i < PassItems; i++) {
            if(findBuf[i] >= sigMax || findBuf[i] <= sigMin) {
                sbChannel->setValue(i % NumChannels);
                changePos(pos);
                return;
            }
        }
    }
    if(pos < 0)
        changePos(0);
    else if(pos > fileSize)
        changePos(pos - PassBytes);
}

void SigParamSaturationDialog::on_btnLeft_clicked()
{
    findNextSpot(-1);
}

void SigParamSaturationDialog::on_btnRight_clicked()
{
    findNextSpot(+1);
}
