TEMPLATE = lib
CONFIG = staticlib
SOURCES = dSFMT.c \
    entropy.c
HEADERS = dSFMT.h dSFMT-params.h dSFMT-params19937.h \
    entropy.h

QMAKE_CFLAGS += -msse2 -DDSFMT_MEXP=19937 -DHAVE_SSE2
