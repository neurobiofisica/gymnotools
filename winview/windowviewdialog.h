#ifndef WINDOWVIEWDIALOG_H
#define WINDOWVIEWDIALOG_H

#include <QDialog>
#include <QModelIndex>
#include <QListWidgetItem>

class CustomPlotCurve;
class CustomPlotZoomer;
class QwtPlotPanner;
class QwtScaleDiv;
class WindowFile;
class ResizableBuffer;

namespace Ui {
    class WindowViewDialog;
}

class WindowViewDialog : public QDialog
{
    Q_OBJECT

public:
    explicit WindowViewDialog(WindowFile &infile, const QString &origFilename,
                              int winatatime, QWidget *parent = 0);
    ~WindowViewDialog();

private slots:
    void on_listWins_customContextMenuRequested(const QPoint &pos);
    void on_enableNorm_clicked();
    void on_btnLeft_clicked();
    void on_btnRight_clicked();
    void on_btnGo_clicked();
    void contextMenu_copyTime();
    void contextMenu_showOriginal();
    void listRect();

private:
    void plotBegin();
    void plotCurrent();
    void plotEnd();

    Ui::WindowViewDialog *ui;

    CustomPlotZoomer *zoomer;
    QwtPlotPanner *panner;

    int validCurves;
    CustomPlotCurve **curves;
    double **ydata;
    double **xdata;
    float *readbuf;

    WindowFile &file;
    const QString &origfile;
    const int winsPerScreen;
};

#endif // WINDOWVIEWDIALOG_H
