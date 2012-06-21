QT += gui core

TEMPLATE = lib
CONFIG = qt staticlib

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
