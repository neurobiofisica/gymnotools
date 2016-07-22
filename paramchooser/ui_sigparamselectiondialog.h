/********************************************************************************
** Form generated from reading UI file 'sigparamselectiondialog.ui'
**
** Created by: Qt User Interface Compiler version 4.8.6
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_SIGPARAMSELECTIONDIALOG_H
#define UI_SIGPARAMSELECTIONDIALOG_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QDialog>
#include <QtGui/QDialogButtonBox>
#include <QtGui/QHBoxLayout>
#include <QtGui/QHeaderView>
#include <QtGui/QSpacerItem>
#include <QtGui/QToolButton>
#include <QtGui/QVBoxLayout>
#include <QtGui/QWidget>
#include "qwt_plot.h"

QT_BEGIN_NAMESPACE

class Ui_SigParamSelectionDialog
{
public:
    QVBoxLayout *verticalLayout;
    QWidget *widget;
    QHBoxLayout *horizontalLayout;
    QToolButton *btnGo;
    QSpacerItem *horizontalSpacer;
    QWidget *paramArea;
    QHBoxLayout *paramAreaLayout;
    QSpacerItem *horizontalSpacer_2;
    QToolButton *btnWaveform;
    QWidget *widget_2;
    QHBoxLayout *horizontalLayout_2;
    QToolButton *btnLeft;
    QwtPlot *plot;
    QToolButton *btnRight;
    QDialogButtonBox *buttonBox;

    void setupUi(QDialog *SigParamSelectionDialog)
    {
        if (SigParamSelectionDialog->objectName().isEmpty())
            SigParamSelectionDialog->setObjectName(QString::fromUtf8("SigParamSelectionDialog"));
        SigParamSelectionDialog->resize(548, 341);
        verticalLayout = new QVBoxLayout(SigParamSelectionDialog);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        widget = new QWidget(SigParamSelectionDialog);
        widget->setObjectName(QString::fromUtf8("widget"));
        horizontalLayout = new QHBoxLayout(widget);
        horizontalLayout->setSpacing(0);
        horizontalLayout->setContentsMargins(0, 0, 0, 0);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        btnGo = new QToolButton(widget);
        btnGo->setObjectName(QString::fromUtf8("btnGo"));
        QIcon icon;
        icon.addFile(QString::fromUtf8(":/icon/go"), QSize(), QIcon::Normal, QIcon::Off);
        btnGo->setIcon(icon);

        horizontalLayout->addWidget(btnGo);

        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout->addItem(horizontalSpacer);

        paramArea = new QWidget(widget);
        paramArea->setObjectName(QString::fromUtf8("paramArea"));
        paramAreaLayout = new QHBoxLayout(paramArea);
        paramAreaLayout->setContentsMargins(0, 0, 0, 0);
        paramAreaLayout->setObjectName(QString::fromUtf8("paramAreaLayout"));

        horizontalLayout->addWidget(paramArea);

        horizontalSpacer_2 = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout->addItem(horizontalSpacer_2);

        btnWaveform = new QToolButton(widget);
        btnWaveform->setObjectName(QString::fromUtf8("btnWaveform"));
        QIcon icon1;
        icon1.addFile(QString::fromUtf8(":/icon/waveform"), QSize(), QIcon::Normal, QIcon::Off);
        btnWaveform->setIcon(icon1);

        horizontalLayout->addWidget(btnWaveform);


        verticalLayout->addWidget(widget);

        widget_2 = new QWidget(SigParamSelectionDialog);
        widget_2->setObjectName(QString::fromUtf8("widget_2"));
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Expanding);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(widget_2->sizePolicy().hasHeightForWidth());
        widget_2->setSizePolicy(sizePolicy);
        horizontalLayout_2 = new QHBoxLayout(widget_2);
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        horizontalLayout_2->setContentsMargins(0, 9, 0, 9);
        btnLeft = new QToolButton(widget_2);
        btnLeft->setObjectName(QString::fromUtf8("btnLeft"));
        QIcon icon2;
        icon2.addFile(QString::fromUtf8(":/icon/left"), QSize(), QIcon::Normal, QIcon::Off);
        btnLeft->setIcon(icon2);

        horizontalLayout_2->addWidget(btnLeft);

        plot = new QwtPlot(widget_2);
        plot->setObjectName(QString::fromUtf8("plot"));

        horizontalLayout_2->addWidget(plot);

        btnRight = new QToolButton(widget_2);
        btnRight->setObjectName(QString::fromUtf8("btnRight"));
        QIcon icon3;
        icon3.addFile(QString::fromUtf8(":/icon/right"), QSize(), QIcon::Normal, QIcon::Off);
        btnRight->setIcon(icon3);

        horizontalLayout_2->addWidget(btnRight);


        verticalLayout->addWidget(widget_2);

        buttonBox = new QDialogButtonBox(SigParamSelectionDialog);
        buttonBox->setObjectName(QString::fromUtf8("buttonBox"));
        buttonBox->setOrientation(Qt::Horizontal);
        buttonBox->setStandardButtons(QDialogButtonBox::Cancel|QDialogButtonBox::Ok);

        verticalLayout->addWidget(buttonBox);

        QWidget::setTabOrder(buttonBox, btnLeft);
        QWidget::setTabOrder(btnLeft, btnRight);
        QWidget::setTabOrder(btnRight, btnGo);
        QWidget::setTabOrder(btnGo, btnWaveform);

        retranslateUi(SigParamSelectionDialog);
        QObject::connect(buttonBox, SIGNAL(accepted()), SigParamSelectionDialog, SLOT(accept()));
        QObject::connect(buttonBox, SIGNAL(rejected()), SigParamSelectionDialog, SLOT(reject()));

        QMetaObject::connectSlotsByName(SigParamSelectionDialog);
    } // setupUi

    void retranslateUi(QDialog *SigParamSelectionDialog)
    {
        SigParamSelectionDialog->setWindowTitle(QApplication::translate("SigParamSelectionDialog", "Dialog", 0, QApplication::UnicodeUTF8));
#ifndef QT_NO_TOOLTIP
        btnGo->setToolTip(QApplication::translate("SigParamSelectionDialog", "Jump to a specific position (in time) of the displayed signal (Alt+G)", 0, QApplication::UnicodeUTF8));
#endif // QT_NO_TOOLTIP
        btnGo->setText(QString());
        btnGo->setShortcut(QApplication::translate("SigParamSelectionDialog", "Alt+G", 0, QApplication::UnicodeUTF8));
#ifndef QT_NO_TOOLTIP
        btnWaveform->setToolTip(QApplication::translate("SigParamSelectionDialog", "View original signal time domain waveforms in all channels (Alt+S)", 0, QApplication::UnicodeUTF8));
#endif // QT_NO_TOOLTIP
        btnWaveform->setText(QString());
        btnWaveform->setShortcut(QApplication::translate("SigParamSelectionDialog", "Alt+S", 0, QApplication::UnicodeUTF8));
        btnLeft->setText(QString());
        btnLeft->setShortcut(QApplication::translate("SigParamSelectionDialog", "Left", 0, QApplication::UnicodeUTF8));
        btnRight->setText(QString());
        btnRight->setShortcut(QApplication::translate("SigParamSelectionDialog", "Right", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class SigParamSelectionDialog: public Ui_SigParamSelectionDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_SIGPARAMSELECTIONDIALOG_H
