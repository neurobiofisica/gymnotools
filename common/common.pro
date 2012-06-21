QT += core
QT -= gui

TEMPLATE = lib
CONFIG = qt staticlib

SOURCES = \ 
    sigutil.cpp \
    signalbuffer.cpp \
    signalfile.cpp
HEADERS = sigcfg.h \
    sigutil.h \
    resizablebuffer.h \
    signalbuffer.h \
    signalfile.h
