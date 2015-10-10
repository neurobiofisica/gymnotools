#-------------------------------------------------
#
# Project created by QtCreator 2015-10-09T17:38:22
#
#-------------------------------------------------

QT       -= core gui

TARGET = exportSym
TEMPLATE = lib

DEFINES += EXPORTSYM_LIBRARY

SOURCES += exportSym.cpp

HEADERS += exportSym.h\
        exportsym_global.h

unix {
    target.path = /usr/lib
    INSTALLS += target
}
