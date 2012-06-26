QT += core
QT -= gui

TEMPLATE = lib
CONFIG += staticlib
CONFIG -= debug_and_release debug_and_release_target

SOURCES = \ 
    sigutil.cpp \
    signalbuffer.cpp \
    signalfile.cpp \
    excludedintervals.cpp \
    cutincomplete.cpp
HEADERS = sigcfg.h \
    sigutil.h \
    resizablebuffer.h \
    signalbuffer.h \
    signalfile.h \
    commoninit.h \
    defaultparams.h \
    excludedintervals.h \
    cutincomplete.h
