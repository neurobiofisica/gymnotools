#include "windowviewdialog.h"
#include "ui_windowviewdialog.h"

#include <math.h>
#include <QMenu>
#include <QRegExp>
#include <QInputDialog>
#include <qwt_plot_curve.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_panner.h>
#include <qwt_clipper.h>
#include "common/sigcfg.h"

static const int WinMaxSamples = 16*EODSamples;

class CustomPlotCurve : public QwtPlotCurve
{
public:
    double time;
    int channel;
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
    file(infile),
    origfile(origFilename),
    winsPerScreen(winatatime)
{
    ui->setupUi(this);

    ui->plot->setCanvasBackground(QColor(Qt::black));
    ui->plot->canvas()->setCursor(Qt::ArrowCursor);

    zoomer = new CustomPlotZoomer(ui->plot->canvas());
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
        curves[i]->attach(ui->plot);
    }

    xdata = new double[WinMaxSamples];
    ydata = new double*[winsPerScreen];
    ydata[0] = new double[winsPerScreen * WinMaxSamples];
    for(int i = 1; i < winsPerScreen; i++)
        ydata[i] = &ydata[i-1][WinMaxSamples];
}

WindowViewDialog::~WindowViewDialog()
{
    delete ui;
    delete [] curves;
    delete [] xdata;
    delete [] ydata[0];
    delete [] ydata;
}

void WindowViewDialog::on_listWins_customContextMenuRequested(const QPoint &pos)
{
    QListWidget *list = ui->listWins;
    if(list->currentItem() != NULL) {
        QMenu menu(this);
        menu.addAction("Copy &time",
                       this, SLOT(contextMenu_copyTime()));
        QAction *sOrig = menu.addAction("Show &original",
                                        this, SLOT(contextMenu_showOriginal()));
        if(origfile.isEmpty())
            sOrig->setEnabled(false);
        menu.exec(list->mapToGlobal(pos));
    }
}

void WindowViewDialog::on_enableNorm_clicked()
{
}

void WindowViewDialog::on_btnLeft_clicked()
{
}

void WindowViewDialog::on_btnRight_clicked()
{
}

void WindowViewDialog::on_btnGo_clicked()
{
}

void WindowViewDialog::contextMenu_copyTime()
{
}

void WindowViewDialog::contextMenu_showOriginal()
{
}

void WindowViewDialog::listRect()
{
}
