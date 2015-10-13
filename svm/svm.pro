TEMPLATE = lib
CONFIG = staticlib
SOURCES = svm.cpp
HEADERS = svm.h

QMAKE_CXXFLAGS += -fopenmp -Wno-unused-result -D_DENSE_REP
QMAKE_LFLAGS += -fopenmp
