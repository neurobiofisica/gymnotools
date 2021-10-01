#ifndef COMMONINIT_H
#define COMMONINIT_H

#include <locale.h>

static void commonInit() {
    setlocale(LC_NUMERIC, "C");
}

#endif // COMMONINIT_H
