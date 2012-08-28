QT += core
QT -= gui

TARGET = singlefish
TEMPLATE = app

SOURCES += \ 
    main.cpp

HEADERS += 

CONFIG += console
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -L../svm -lsvm
LIBS += -L../dtcwpt -ldtcwpt
LIBS += -lfftw3f

QMAKE_CXXFLAGS += -fopenmp
QMAKE_LFLAGS += -fopenmp
