QT += core
QT -= gui

TARGET = recog
TEMPLATE = app

SOURCES += \ 
    main.cpp

HEADERS += 

CONFIG += console
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -ldb-5.1

QMAKE_CXXFLAGS += -fopenmp
QMAKE_LFLAGS += -fopenmp
