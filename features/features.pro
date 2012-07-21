QT += core
QT -= gui

TARGET = features
TEMPLATE = app

SOURCES += \ 
    main.cpp

HEADERS += 

CONFIG += console
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -L../dtcwpt -ldtcwpt
LIBS += -lfftw3f
