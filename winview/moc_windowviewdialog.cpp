/****************************************************************************
** Meta object code from reading C++ file 'windowviewdialog.h'
**
** Created by: The Qt Meta Object Compiler version 63 (Qt 4.8.6)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "windowviewdialog.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'windowviewdialog.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.6. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_WindowViewDialog[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       8,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      22,   18,   17,   17, 0x08,
      69,   17,   17,   17, 0x08,
      93,   17,   17,   17, 0x08,
     114,   17,   17,   17, 0x08,
     136,   17,   17,   17, 0x08,
     155,   17,   17,   17, 0x08,
     178,   17,   17,   17, 0x08,
     205,   17,   17,   17, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_WindowViewDialog[] = {
    "WindowViewDialog\0\0pos\0"
    "on_listWins_customContextMenuRequested(QPoint)\0"
    "on_enableNorm_clicked()\0on_btnLeft_clicked()\0"
    "on_btnRight_clicked()\0on_btnGo_clicked()\0"
    "contextMenu_copyTime()\0"
    "contextMenu_showOriginal()\0listRect()\0"
};

void WindowViewDialog::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        WindowViewDialog *_t = static_cast<WindowViewDialog *>(_o);
        switch (_id) {
        case 0: _t->on_listWins_customContextMenuRequested((*reinterpret_cast< const QPoint(*)>(_a[1]))); break;
        case 1: _t->on_enableNorm_clicked(); break;
        case 2: _t->on_btnLeft_clicked(); break;
        case 3: _t->on_btnRight_clicked(); break;
        case 4: _t->on_btnGo_clicked(); break;
        case 5: _t->contextMenu_copyTime(); break;
        case 6: _t->contextMenu_showOriginal(); break;
        case 7: _t->listRect(); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData WindowViewDialog::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject WindowViewDialog::staticMetaObject = {
    { &QDialog::staticMetaObject, qt_meta_stringdata_WindowViewDialog,
      qt_meta_data_WindowViewDialog, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &WindowViewDialog::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *WindowViewDialog::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *WindowViewDialog::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_WindowViewDialog))
        return static_cast<void*>(const_cast< WindowViewDialog*>(this));
    return QDialog::qt_metacast(_clname);
}

int WindowViewDialog::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 8)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 8;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
