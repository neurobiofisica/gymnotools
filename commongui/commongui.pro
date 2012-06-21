QT += gui core

TEMPLATE = lib
CONFIG += staticlib
CONFIG -= debug_and_release debug_and_release_target

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
