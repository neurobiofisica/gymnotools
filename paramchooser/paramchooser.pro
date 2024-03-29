QT       += core gui

TARGET = paramchooser
TEMPLATE = app

RESOURCES += \
    resource.qrc

SOURCES += \
    main.cpp \
    sigparamselectiondialog.cpp \
    fileminmaxfinder.cpp

HEADERS += \
    sigparamselectiondialog.h \
    progressthread.h \
    fileminmaxfinder.h

FORMS += \
    sigparamselectiondialog.ui

CONFIG += qwt console
INCLUDEPATH += ..
LIBS += -L../common -lcommon
LIBS += -L../commongui -lcommongui
