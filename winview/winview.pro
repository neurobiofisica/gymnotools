QT       += core gui

TARGET = winview
TEMPLATE = app

RESOURCES += \ 
    resource.qrc

SOURCES += \ 
    main.cpp \
    windowviewdialog.cpp

HEADERS += \ 
    windowviewdialog.h

FORMS += \ 
    windowviewdialog.ui

CONFIG += qwt console
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -L../commongui -lcommongui
