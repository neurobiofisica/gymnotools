#include <QFile>

#include <qwt_plot_curve.h>
#include <qwt_plot_canvas.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_panner.h>

#include "vieworiginalsignaldialog.h"
#include "ui_vieworiginalsignaldialog.h"

#include "guicfg.h"
#include "guiutil.h"

static const int ReadBufLen = PlotDialogNumPoints*NumChannels;

ViewOriginalSignalDialog::ViewOriginalSignalDialog(const QString &filename, qint64 curPos, int channel, QWidget *parent) :
    QDialog(parent),
    ui(new Ui::ViewOriginalSignalDialog)
{
    QFile file(filename);
    file.open(QFile::ReadOnly);
    file.seek(curPos);

    readBuf = new float[ReadBufLen];
    xdata = new double[PlotDialogNumPoints];
    ydata = new double[PlotDialogNumPoints];

    fillXData(xdata, curPos);

    memset(readBuf, 0, ReadBufLen*sizeof(float));
    file.read((char*)readBuf, ReadBufLen*sizeof(float));
    file.close();

    ui->setupUi(this);

    ui->plot->setCanvasBackground(QColor(Qt::black));
    ui->plot->canvas()->setCursor(Qt::ArrowCursor);

    curve = new QwtPlotCurve();
    curve->setRenderHint(QwtPlotItem::RenderAntialiased);
    curve->setPen(QColor(Qt::green));
    curve->attach(ui->plot);

    zoomer = new QwtPlotZoomer(ui->plot->canvas());
    zoomer->setRubberBandPen(QColor(Qt::blue));
    zoomer->setTrackerPen(QColor(Qt::white));
    zoomer->setMousePattern(QwtEventPattern::MouseSelect2, Qt::RightButton, Qt::ControlModifier);
    zoomer->setMousePattern(QwtEventPattern::MouseSelect3, Qt::RightButton);

    panner = new QwtPlotPanner(ui->plot->canvas());
    panner->setMouseButton(Qt::MidButton);

    ui->spinChannel->setValue(channel);
    on_spinChannel_valueChanged(channel);
}

ViewOriginalSignalDialog::~ViewOriginalSignalDialog()
{
    delete ui;
    delete [] readBuf;
    delete [] xdata;
    delete [] ydata;
}

void ViewOriginalSignalDialog::on_spinChannel_valueChanged(int channel)
{
    for(int i = channel, j = 0; i < ReadBufLen; i += NumChannels, j++)
        ydata[j] = readBuf[i];

    // set autoscale back (may have been unset by zoomer)
    ui->plot->setAxisAutoScale(QwtPlot::xBottom);
    ui->plot->setAxisAutoScale(QwtPlot::yLeft);

    curve->setRawSamples(xdata, ydata, PlotDialogNumPoints);

    ui->plot->replot();
    zoomer->setZoomBase();
}
