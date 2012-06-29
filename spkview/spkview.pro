QT       += core gui

TARGET = spkview
TEMPLATE = app

RESOURCES += 

SOURCES += \ 
    main.cpp

HEADERS += 

FORMS += 

CONFIG += qwt console
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -L../commongui -lcommongui
