#ifndef EXPORTSYM_GLOBAL_H
#define EXPORTSYM_GLOBAL_H

#include <QtCore/qglobal.h>

#if defined(EXPORTSYM_LIBRARY)
#  define EXPORTSYMSHARED_EXPORT Q_DECL_EXPORT
#else
#  define EXPORTSYMSHARED_EXPORT Q_DECL_IMPORT
#endif

#endif // EXPORTSYM_GLOBAL_H
