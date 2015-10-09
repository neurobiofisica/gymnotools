#include "windowviewdialog.h"
#include "ui_windowviewdialog.h"

#include <math.h>
#include <QMenu>
#include <QRegExp>
#include <QInputDialog>
#include <QClipboard>
#include <qwt_plot_canvas.h>
#include <qwt_plot_curve.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_panner.h>
#include <qwt_clipper.h>

#include <qwt_symbol.h>

#include "common/windowfile.h"
#include "common/sigcfg.h"
#include "common/sigutil.h"
#include "commongui/vieworiginalsignaldialog.h"

static const int WinMaxSamples = 16*EODSamples;

class CustomPlotCurve : public QwtPlotCurve
{
public:
    double time;
    int channel;
    int samples;
};

class CustomPlotZoomer : public QwtPlotZoomer
{
public:
    explicit CustomPlotZoomer(QwtPlotCanvas *canvas, bool doReplot=true)
        :QwtPlotZoomer(canvas, doReplot) { }
    QRectF getScaleRect() const { return scaleRect(); }
};

WindowViewDialog::WindowViewDialog(WindowFile &infile, const QString &origFilename,
                                   int winatatime, QWidget *parent) :
    QDialog(parent),
    ui(new Ui::WindowViewDialog),
    validCurves(0),
    file(infile),
    origfile(origFilename),
    winsPerScreen(winatatime)
{
    ui->setupUi(this);

    ui->plot->setCanvasBackground(QColor(Qt::black));
    ui->plot->canvas()->setCursor(Qt::ArrowCursor);

    zoomer = new CustomPlotZoomer((QwtPlotCanvas*)ui->plot->canvas());
    zoomer->setRubberBandPen(QColor(Qt::blue));
    zoomer->setTrackerPen(QColor(Qt::white));
    zoomer->setMousePattern(QwtEventPattern::MouseSelect2, Qt::RightButton,
                            Qt::ControlModifier);
    zoomer->setMousePattern(QwtEventPattern::MouseSelect3, Qt::RightButton);

    panner = new QwtPlotPanner(ui->plot->canvas());
    panner->setMouseButton(Qt::MidButton);

    QObject::connect(zoomer, SIGNAL(zoomed(QRectF)), this, SLOT(listRect()));
    QObject::connect(panner, SIGNAL(panned(int,int)), this, SLOT(listRect()));

    curves = new CustomPlotCurve*[winsPerScreen];
    for(int i = 0; i < winsPerScreen; i++) {
        curves[i] = new CustomPlotCurve();
        curves[i]->setRenderHint(QwtPlotItem::RenderAntialiased);
        curves[i]->setPen(QColor(Qt::green));

        QwtSymbol *symbol = new QwtSymbol( QwtSymbol::Ellipse, QBrush(Qt::green), QPen(Qt::green, 1), QSize(2,2) );
        curves[i]->setSymbol(symbol);

        curves[i]->attach(ui->plot);
    }

    xdata = new double*[winsPerScreen];
    ydata = new double*[winsPerScreen];
    xdata[0] = new double[winsPerScreen * WinMaxSamples];
    ydata[0] = new double[winsPerScreen * WinMaxSamples];
    for(int i = 1; i < winsPerScreen; i++) {
        xdata[i] = &xdata[i-1][WinMaxSamples];
        ydata[i] = &ydata[i-1][WinMaxSamples];
    }
    readbuf = new float[WinMaxSamples];

    goForward();
}

WindowViewDialog::~WindowViewDialog()
{
    delete ui;
    delete [] curves;
    delete [] xdata[0];
    delete [] xdata;
    delete [] ydata[0];
    delete [] ydata;
    delete [] readbuf;
}

void WindowViewDialog::on_listWins_customContextMenuRequested(const QPoint &pos)
{
    QListWidget *list = ui->listWins;
    if(list->currentItem() != NULL) {
        QMenu menu(this);
        QAction *sOrig = menu.addAction("Show &original",
                                        this, SLOT(contextMenu_showOriginal()));
        if(origfile.isEmpty())
            sOrig->setEnabled(false);
        menu.addAction("Copy &time",
                       this, SLOT(contextMenu_copyTime()));
        menu.exec(list->mapToGlobal(pos));
    }
}

void WindowViewDialog::plotBegin()
{
    ui->listWins->clear();
    ui->plot->setAxisAutoScale(QwtPlot::xBottom);
    ui->plot->setAxisAutoScale(QwtPlot::yLeft);
    validCurves = 0;
}

void WindowViewDialog::plotCurrent()
{
    const bool normalize = ui->enableNorm->isChecked();

    int samples = qMin(file.getEventSamples(), WinMaxSamples);
    file.read((char *)readbuf, samples*sizeof(float));

    float norm = 1.;
    if(normalize)
        norm = 1./maxAbsFloat(readbuf, samples);

    double *data = ydata[validCurves];
    for(int i = 0; i < samples; i++)
        data[i] = norm*readbuf[i];

    curves[validCurves]->time = ((double)file.getEventOffset())/
            ((double)BytesPerSample*SamplingRate);
    curves[validCurves]->channel = file.getChannelId();
    curves[validCurves]->samples = samples;

    ++validCurves;
}

void WindowViewDialog::plotEnd()
{
    int maxSamples = 0;
    for(int i = 0; i < validCurves; i++) {
        if(curves[i]->samples > maxSamples) {
            maxSamples = curves[i]->samples;
        }
    }

    const double samplingPeriod = 1./SamplingRate;
    for(int i = 0; i < validCurves; i++) {
        const int samples = curves[i]->samples;
        const double xoff = 0.5*(double)(maxSamples - samples);
        double *ax = xdata[i];
        for(int j = 0; j < samples; j++) {
            ax[j] = samplingPeriod * (xoff + j);
        }
        curves[i]->setRawSamples(ax, ydata[i], samples);
    }

    for(int i = 0; i < winsPerScreen; i++)
        curves[i]->setVisible(i < validCurves);
    zoomer->setZoomBase();
}

void WindowViewDialog::rewindFile()
{
    if(justMovedForward) {
        for(int i = 0; i < validCurves; i++) {
            file.prevChannel();
        }
    }
    else {
        for(int i = 0; i < validCurves; i++) {
            file.nextChannel();
        }
    }
}

void WindowViewDialog::goForward()
{
    plotBegin();
    for(int i = 0; (i < winsPerScreen) && file.nextChannel(); i++) {
        plotCurrent();
    }
    plotEnd();
    justMovedForward = true;
}

void WindowViewDialog::goBackward()
{
    plotBegin();
    for(int i = 0; (i < winsPerScreen) && file.prevChannel(); i++) {
        plotCurrent();
    }
    plotEnd();
    justMovedForward = false;
}

void WindowViewDialog::replotCurves()
{
    rewindFile();
    if(justMovedForward) {
        goForward();
    }
    else {
        goBackward();
    }
}

void WindowViewDialog::on_enableNorm_clicked()
{
    replotCurves();
}

void WindowViewDialog::on_btnLeft_clicked()
{
    if(justMovedForward)
        rewindFile();
    goBackward();
}

void WindowViewDialog::on_btnRight_clicked()
{
    if(!justMovedForward)
        rewindFile();
    goForward();
}

void WindowViewDialog::on_btnGo_clicked()
{
    double t = 0.;
    if(validCurves > 0)
        t = qMin(curves[0]->time, curves[validCurves-1]->time);

    bool ok;
    t = QInputDialog::getDouble(this, "Go to", "Jump to time (in seconds):",
                                t, 0, 2e9, 3, &ok);
    if(!ok)
        return;

    qint64 desiredOffset = qint64(t * SamplingRate) * BytesPerSample;
    while((file.getEventOffset() >= desiredOffset) && file.prevEvent());
    while((file.getEventOffset() < desiredOffset) && file.nextEvent());
    goForward();
}

void WindowViewDialog::contextMenu_copyTime()
{
    double t;
    int ch;
    if(!getListSelection(t, ch))
        return;
    QApplication::clipboard()->setText(
                QString("%1").arg(t,0,'f',3));
}

void WindowViewDialog::contextMenu_showOriginal()
{
    if(origfile.isEmpty())
        return;

    double t;
    int ch;
    if(!getListSelection(t, ch))
        return;

    ViewOriginalSignalDialog dlg(origfile,
                                 qint64(t * SamplingRate) * BytesPerSample,
                                 ch,
                                 this);
    dlg.exec();
}

bool WindowViewDialog::getListSelection(double &t, int &ch)
{
    const QListWidget *list = ui->listWins;
    const QListWidgetItem *item = list->currentItem();
    if(item == NULL)
        return false;
    const QString data = item->data(Qt::DisplayRole).toString();

    QRegExp rx("t=([0-9.]+)s, ch=([0-9]+)");
    if(!rx.exactMatch(data))
        return false;

    t = rx.cap(1).toDouble();
    ch = rx.cap(2).toInt();
    return true;
}

void WindowViewDialog::listRect()
{
    const QRectF rect = zoomer->getScaleRect();
    QListWidget *list = ui->listWins;
    QString templ("t=%1s, ch=%2");
    list->clear();
    for(int i = 0; i < validCurves; i++) {
        const double *ax = xdata[i];
        const double *ay = ydata[i];
        QPolygonF poly;
        for(int j = 0; j < curves[i]->samples; j++)
            poly << QPointF(ax[j], ay[j]);
        if(!QwtClipper::clipPolygonF(rect, poly).empty()) {
            const double time = curves[i]->time;
            const int channel = curves[i]->channel;
            list->addItem(templ.arg(time,0,'f',3).arg(channel));
        }
    }
}
