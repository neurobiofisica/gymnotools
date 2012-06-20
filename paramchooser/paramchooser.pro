QT       += core gui

TARGET = paramchooser
TEMPLATE = app

CONFIG += qwt

RESOURCES += \
    resource.qrc

HEADERS += \
    guicfg.h

INCLUDEPATH += ..
LIBS += -L../common -lcommon

SOURCES += \
    main.cpp
