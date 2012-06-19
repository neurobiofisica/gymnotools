TEMPLATE = lib
CONFIG = staticlib
SOURCES = svm.cpp
HEADERS = svm.h

QMAKE_CXXFLAGS += -fopenmp -Wno-unused-result
QMAKE_LFLAGS += -fopenmp
