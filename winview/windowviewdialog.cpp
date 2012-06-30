#include "windowviewdialog.h"
#include "ui_windowviewdialog.h"

#include <QRegExp>
#include <QInputDialog>
#include <qwt_plot_curve.h>
#include <qwt_plot_zoomer.h>
#include <qwt_plot_panner.h>
#include <qwt_clipper.h>
#include <math.h>

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

WindowViewDialog::WindowViewDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::WindowViewDialog)
{
    ui->setupUi(this);

    ui->plot->setCanvasBackground(QColor(Qt::black));
    ui->plot->canvas()->setCursor(Qt::ArrowCursor);

    zoomer = new CustomPlotZoomer(ui->plot->canvas());
    zoomer->setRubberBandPen(QColor(Qt::blue));
    zoomer->setTrackerPen(QColor(Qt::white));
    zoomer->setMousePattern(QwtEventPattern::MouseSelect2, Qt::RightButton, Qt::ControlModifier);
    zoomer->setMousePattern(QwtEventPattern::MouseSelect3, Qt::RightButton);

    panner = new QwtPlotPanner(ui->plot->canvas());
    panner->setMouseButton(Qt::MidButton);

    //QObject::connect(zoomer, SIGNAL(zoomed(QRectF)), this, SLOT(listRect()));
    //QObject::connect(panner, SIGNAL(panned(int,int)), this, SLOT(listRect()));
}

WindowViewDialog::~WindowViewDialog()
{
    delete ui;
}

void WindowViewDialog::on_listEODs_customContextMenuRequested(const QPoint &pos)
{
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
