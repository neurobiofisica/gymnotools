#ifndef WINDOWVIEWDIALOG_H
#define WINDOWVIEWDIALOG_H

#include <QDialog>
#include <QModelIndex>
#include <QListWidgetItem>

class CustomPlotCurve;
class CustomPlotZoomer;
class QwtPlotPanner;
class QwtScaleDiv;

namespace Ui {
    class WindowViewDialog;
}

class WindowViewDialog : public QDialog
{
    Q_OBJECT

public:
    explicit WindowViewDialog(QWidget *parent = 0);
    ~WindowViewDialog();

private slots:
    void on_listEODs_customContextMenuRequested(const QPoint &pos);
    void on_enableNorm_clicked();
    void on_btnLeft_clicked();
    void on_btnRight_clicked();
    void on_btnGo_clicked();

private:
    void startDrawingEODs();
    void drawOneEOD(int &firstCurveIndex, qint64 pos);
    void finishDrawingEODs(int firstCurveIndex);
    void drawAllNext();
    void drawAllPrev();

    Ui::WindowViewDialog *ui;

    CustomPlotZoomer *zoomer;
    QwtPlotPanner *panner;
};

#endif // WINDOWVIEWDIALOG_H
