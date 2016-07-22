/********************************************************************************
** Form generated from reading UI file 'vieworiginalsignaldialog.ui'
**
** Created by: Qt User Interface Compiler version 4.8.6
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_VIEWORIGINALSIGNALDIALOG_H
#define UI_VIEWORIGINALSIGNALDIALOG_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QDialog>
#include <QtGui/QHBoxLayout>
#include <QtGui/QHeaderView>
#include <QtGui/QLabel>
#include <QtGui/QSpacerItem>
#include <QtGui/QSpinBox>
#include <QtGui/QVBoxLayout>
#include <QtGui/QWidget>
#include "qwt_plot.h"

QT_BEGIN_NAMESPACE

class Ui_ViewOriginalSignalDialog
{
public:
    QVBoxLayout *verticalLayout;
    QWidget *widget;
    QHBoxLayout *horizontalLayout;
    QSpacerItem *horizontalSpacer;
    QLabel *label;
    QSpinBox *spinChannel;
    QSpacerItem *horizontalSpacer_2;
    QwtPlot *plot;

    void setupUi(QDialog *ViewOriginalSignalDialog)
    {
        if (ViewOriginalSignalDialog->objectName().isEmpty())
            ViewOriginalSignalDialog->setObjectName(QString::fromUtf8("ViewOriginalSignalDialog"));
        ViewOriginalSignalDialog->resize(483, 311);
        verticalLayout = new QVBoxLayout(ViewOriginalSignalDialog);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        widget = new QWidget(ViewOriginalSignalDialog);
        widget->setObjectName(QString::fromUtf8("widget"));
        horizontalLayout = new QHBoxLayout(widget);
#ifndef Q_OS_MAC
        horizontalLayout->setSpacing(6);
#endif
        horizontalLayout->setContentsMargins(0, 0, 0, 0);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout->addItem(horizontalSpacer);

        label = new QLabel(widget);
        label->setObjectName(QString::fromUtf8("label"));

        horizontalLayout->addWidget(label);

        spinChannel = new QSpinBox(widget);
        spinChannel->setObjectName(QString::fromUtf8("spinChannel"));
        spinChannel->setMaximum(6);

        horizontalLayout->addWidget(spinChannel);

        horizontalSpacer_2 = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout->addItem(horizontalSpacer_2);


        verticalLayout->addWidget(widget);

        plot = new QwtPlot(ViewOriginalSignalDialog);
        plot->setObjectName(QString::fromUtf8("plot"));

        verticalLayout->addWidget(plot);


        retranslateUi(ViewOriginalSignalDialog);

        QMetaObject::connectSlotsByName(ViewOriginalSignalDialog);
    } // setupUi

    void retranslateUi(QDialog *ViewOriginalSignalDialog)
    {
        ViewOriginalSignalDialog->setWindowTitle(QApplication::translate("ViewOriginalSignalDialog", "Original signal", 0, QApplication::UnicodeUTF8));
        label->setText(QApplication::translate("ViewOriginalSignalDialog", "Channel:", 0, QApplication::UnicodeUTF8));
    } // retranslateUi

};

namespace Ui {
    class ViewOriginalSignalDialog: public Ui_ViewOriginalSignalDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_VIEWORIGINALSIGNALDIALOG_H
