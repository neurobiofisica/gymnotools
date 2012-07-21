QT += core
QT -= gui

TARGET = slice
TEMPLATE = app

SOURCES += \ 
    main.cpp

HEADERS += 

CONFIG += console
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -L../dsfmt -ldsfmt
