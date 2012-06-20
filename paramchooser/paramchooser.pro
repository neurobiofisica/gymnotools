QT       += core gui

TARGET = paramchooser
TEMPLATE = app

RESOURCES += \
    resource.qrc

SOURCES += \
    main.cpp

HEADERS += \
    guicfg.h

CONFIG += qwt
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -L../commongui -lcommongui

