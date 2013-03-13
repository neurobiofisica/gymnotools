QT += core
QT -= gui

TARGET = crosspat
TEMPLATE = app

SOURCES += \ 
    main.cpp

HEADERS += 

CONFIG += console
INCLUDEPATH += ..
LIBS += -L../common -lcommon

QMAKE_CXXFLAGS += -fopenmp
QMAKE_LFLAGS += -fopenmp
