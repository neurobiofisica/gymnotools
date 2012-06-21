#ifndef COMMONINIT_H
#define COMMONINIT_H

#include <QTextCodec>
#include <locale.h>

static void commonInit() {
    QTextCodec::setCodecForCStrings(QTextCodec::codecForName("UTF-8"));
    setlocale(LC_NUMERIC, "C");
}

#endif // COMMONINIT_H
