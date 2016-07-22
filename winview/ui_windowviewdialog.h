/********************************************************************************
** Form generated from reading UI file 'windowviewdialog.ui'
**
** Created by: Qt User Interface Compiler version 4.8.6
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_WINDOWVIEWDIALOG_H
#define UI_WINDOWVIEWDIALOG_H

#include <QtCore/QVariant>
#include <QtGui/QAction>
#include <QtGui/QApplication>
#include <QtGui/QButtonGroup>
#include <QtGui/QCheckBox>
#include <QtGui/QDialog>
#include <QtGui/QHBoxLayout>
#include <QtGui/QHeaderView>
#include <QtGui/QListWidget>
#include <QtGui/QSpacerItem>
#include <QtGui/QToolButton>
#include <QtGui/QVBoxLayout>
#include <QtGui/QWidget>
#include "qwt_plot.h"

QT_BEGIN_NAMESPACE

class Ui_WindowViewDialog
{
public:
    QHBoxLayout *horizontalLayout;
    QWidget *widget;
    QVBoxLayout *verticalLayout;
    QWidget *widget_2;
    QHBoxLayout *horizontalLayout_2;
    QToolButton *btnLeft;
    QSpacerItem *horizontalSpacer;
    QToolButton *btnGo;
    QCheckBox *enableNorm;
    QSpacerItem *horizontalSpacer_2;
    QToolButton *btnRight;
    QwtPlot *plot;
    QListWidget *listWins;

    void setupUi(QDialog *WindowViewDialog)
    {
        if (WindowViewDialog->objectName().isEmpty())
            WindowViewDialog->setObjectName(QString::fromUtf8("WindowViewDialog"));
        WindowViewDialog->resize(728, 419);
        horizontalLayout = new QHBoxLayout(WindowViewDialog);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        widget = new QWidget(WindowViewDialog);
        widget->setObjectName(QString::fromUtf8("widget"));
        verticalLayout = new QVBoxLayout(widget);
        verticalLayout->setSpacing(0);
        verticalLayout->setContentsMargins(0, 0, 0, 0);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        widget_2 = new QWidget(widget);
        widget_2->setObjectName(QString::fromUtf8("widget_2"));
        horizontalLayout_2 = new QHBoxLayout(widget_2);
        horizontalLayout_2->setSpacing(6);
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        horizontalLayout_2->setContentsMargins(0, 0, 0, 2);
        btnLeft = new QToolButton(widget_2);
        btnLeft->setObjectName(QString::fromUtf8("btnLeft"));
        QIcon icon;
        icon.addFile(QString::fromUtf8(":/icon/left"), QSize(), QIcon::Normal, QIcon::Off);
        btnLeft->setIcon(icon);

        horizontalLayout_2->addWidget(btnLeft);

        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout_2->addItem(horizontalSpacer);

        btnGo = new QToolButton(widget_2);
        btnGo->setObjectName(QString::fromUtf8("btnGo"));
        QIcon icon1;
        icon1.addFile(QString::fromUtf8(":/icon/go"), QSize(), QIcon::Normal, QIcon::Off);
        btnGo->setIcon(icon1);

        horizontalLayout_2->addWidget(btnGo);

        enableNorm = new QCheckBox(widget_2);
        enableNorm->setObjectName(QString::fromUtf8("enableNorm"));
        QSizePolicy sizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(enableNorm->sizePolicy().hasHeightForWidth());
        enableNorm->setSizePolicy(sizePolicy);

        horizontalLayout_2->addWidget(enableNorm);

        horizontalSpacer_2 = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout_2->addItem(horizontalSpacer_2);

        btnRight = new QToolButton(widget_2);
        btnRight->setObjectName(QString::fromUtf8("btnRight"));
        QIcon icon2;
        icon2.addFile(QString::fromUtf8(":/icon/right"), QSize(), QIcon::Normal, QIcon::Off);
        btnRight->setIcon(icon2);

        horizontalLayout_2->addWidget(btnRight);


        verticalLayout->addWidget(widget_2);

        plot = new QwtPlot(widget);
        plot->setObjectName(QString::fromUtf8("plot"));
        plot->setMinimumSize(QSize(400, 0));

        verticalLayout->addWidget(plot);


        horizontalLayout->addWidget(widget);

        listWins = new QListWidget(WindowViewDialog);
        listWins->setObjectName(QString::fromUtf8("listWins"));
        listWins->setMinimumSize(QSize(150, 0));
        listWins->setMaximumSize(QSize(200, 16777215));
        listWins->setContextMenuPolicy(Qt::CustomContextMenu);

        horizontalLayout->addWidget(listWins);

        QWidget::setTabOrder(listWins, btnGo);
        QWidget::setTabOrder(btnGo, enableNorm);
        QWidget::setTabOrder(enableNorm, btnLeft);
        QWidget::setTabOrder(btnLeft, btnRight);

        retranslateUi(WindowViewDialog);

        QMetaObject::connectSlotsByName(WindowViewDialog);
    } // setupUi

    void retranslateUi(QDialog *WindowViewDialog)
    {
        WindowViewDialog->setWindowTitle(QApplication::translate("WindowViewDialog", "View windows", 0, QApplication::UnicodeUTF8));
        btnLeft->setText(QString());
        btnLeft->setShortcut(QApplication::translate("WindowViewDialog", "Left", 0, QApplication::UnicodeUTF8));
#ifndef QT_NO_TOOLTIP
        btnGo->setToolTip(QApplication::translate("WindowViewDialog", "Jump to a specific position (in time) of the displayed signal (Alt+G)", 0, QApplication::UnicodeUTF8));
#endif // QT_NO_TOOLTIP
        btnGo->setText(QString());
        btnGo->setShortcut(QApplication::translate("WindowViewDialog", "Alt+G", 0, QApplication::UnicodeUTF8));
#ifndef QT_NO_TOOLTIP
        enableNorm->setToolTip(QApplication::translate("WindowViewDialog", "Normalize the maximum amplitude of each shown EOD to the unit.", 0, QApplication::UnicodeUTF8));
#endif // QT_NO_TOOLTIP
        enableNorm->setText(QApplication::translate("WindowViewDialog", "&Normalize", 0, QApplication::UnicodeUTF8));
        btnRight->setText(QString());
        btnRight->setShortcut(QApplication::translate("WindowViewDialog", "Right", 0, QApplication::UnicodeUTF8));
#ifndef QT_NO_TOOLTIP
        listWins->setToolTip(QApplication::translate("WindowViewDialog", "Time and channel of all curves contained within the graphics zoom rect.", 0, QApplication::UnicodeUTF8));
#endif // QT_NO_TOOLTIP
    } // retranslateUi

};

namespace Ui {
    class WindowViewDialog: public Ui_WindowViewDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_WINDOWVIEWDIALOG_H
