QT += gui core

TEMPLATE = lib
CONFIG += staticlib

HEADERS += \
    vieworiginalsignaldialog.h \
    guicfg.h \
    guiutil.h

SOURCES += \
    vieworiginalsignaldialog.cpp

FORMS += \
    vieworiginalsignaldialog.ui

CONFIG += qwt
INCLUDEPATH += ..
