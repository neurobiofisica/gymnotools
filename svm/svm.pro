TEMPLATE = lib
CONFIG = staticlib
SOURCES = svm.cpp
HEADERS = svm.h

QMAKE_CXXFLAGS += -fopenmp
QMAKE_LFLAGS += -fopenmp
