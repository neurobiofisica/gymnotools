QT += core
QT -= gui

TARGET = svmtool
TEMPLATE = app

SOURCES += \ 
    main.cpp

HEADERS += 

CONFIG += console
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -L../svm -lsvm

QMAKE_CXXFLAGS += -fopenmp -D_DENSE_REP
QMAKE_LFLAGS += -fopenmp
