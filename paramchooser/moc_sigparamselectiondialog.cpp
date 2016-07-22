/****************************************************************************
** Meta object code from reading C++ file 'sigparamselectiondialog.h'
**
** Created by: The Qt Meta Object Compiler version 63 (Qt 4.8.6)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "sigparamselectiondialog.h"
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'sigparamselectiondialog.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 63
#error "This file was generated using the moc from 4.8.6. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
static const uint qt_meta_data_SigParamSelectionDialog[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       5,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      25,   24,   24,   24, 0x09,
      46,   24,   24,   24, 0x09,
      72,   68,   24,   24, 0x09,
      90,   24,   24,   24, 0x08,
     109,   24,   24,   24, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_SigParamSelectionDialog[] = {
    "SigParamSelectionDialog\0\0on_btnLeft_clicked()\0"
    "on_btnRight_clicked()\0pos\0changePos(qint64)\0"
    "on_btnGo_clicked()\0on_btnWaveform_clicked()\0"
};

void SigParamSelectionDialog::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        SigParamSelectionDialog *_t = static_cast<SigParamSelectionDialog *>(_o);
        switch (_id) {
        case 0: _t->on_btnLeft_clicked(); break;
        case 1: _t->on_btnRight_clicked(); break;
        case 2: _t->changePos((*reinterpret_cast< qint64(*)>(_a[1]))); break;
        case 3: _t->on_btnGo_clicked(); break;
        case 4: _t->on_btnWaveform_clicked(); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData SigParamSelectionDialog::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject SigParamSelectionDialog::staticMetaObject = {
    { &QDialog::staticMetaObject, qt_meta_stringdata_SigParamSelectionDialog,
      qt_meta_data_SigParamSelectionDialog, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &SigParamSelectionDialog::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *SigParamSelectionDialog::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *SigParamSelectionDialog::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_SigParamSelectionDialog))
        return static_cast<void*>(const_cast< SigParamSelectionDialog*>(this));
    return QDialog::qt_metacast(_clname);
}

int SigParamSelectionDialog::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 5)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 5;
    }
    return _id;
}
static const uint qt_meta_data_SigParamLowpassDialog[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       2,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      23,   22,   22,   22, 0x08,
      42,   22,   22,   22, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_SigParamLowpassDialog[] = {
    "SigParamLowpassDialog\0\0filtParamChanged()\0"
    "channelChanged()\0"
};

void SigParamLowpassDialog::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        SigParamLowpassDialog *_t = static_cast<SigParamLowpassDialog *>(_o);
        switch (_id) {
        case 0: _t->filtParamChanged(); break;
        case 1: _t->channelChanged(); break;
        default: ;
        }
    }
    Q_UNUSED(_a);
}

const QMetaObjectExtraData SigParamLowpassDialog::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject SigParamLowpassDialog::staticMetaObject = {
    { &SigParamSelectionDialog::staticMetaObject, qt_meta_stringdata_SigParamLowpassDialog,
      qt_meta_data_SigParamLowpassDialog, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &SigParamLowpassDialog::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *SigParamLowpassDialog::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *SigParamLowpassDialog::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_SigParamLowpassDialog))
        return static_cast<void*>(const_cast< SigParamLowpassDialog*>(this));
    return SigParamSelectionDialog::qt_metacast(_clname);
}

int SigParamLowpassDialog::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = SigParamSelectionDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 2)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 2;
    }
    return _id;
}
static const uint qt_meta_data_SigParamThresholdDialog[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       1,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      25,   24,   24,   24, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_SigParamThresholdDialog[] = {
    "SigParamThresholdDialog\0\0replotData()\0"
};

void SigParamThresholdDialog::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        SigParamThresholdDialog *_t = static_cast<SigParamThresholdDialog *>(_o);
        switch (_id) {
        case 0: _t->replotData(); break;
        default: ;
        }
    }
    Q_UNUSED(_a);
}

const QMetaObjectExtraData SigParamThresholdDialog::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject SigParamThresholdDialog::staticMetaObject = {
    { &SigParamSelectionDialog::staticMetaObject, qt_meta_stringdata_SigParamThresholdDialog,
      qt_meta_data_SigParamThresholdDialog, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &SigParamThresholdDialog::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *SigParamThresholdDialog::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *SigParamThresholdDialog::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_SigParamThresholdDialog))
        return static_cast<void*>(const_cast< SigParamThresholdDialog*>(this));
    return SigParamSelectionDialog::qt_metacast(_clname);
}

int SigParamThresholdDialog::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = SigParamSelectionDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 1)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 1;
    }
    return _id;
}
static const uint qt_meta_data_SigParamWithDualThreshold[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       3,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      38,   27,   26,   26, 0x09,
      75,   64,   26,   26, 0x09,
     104,  101,   26,   26, 0x09,

       0        // eod
};

static const char qt_meta_stringdata_SigParamWithDualThreshold[] = {
    "SigParamWithDualThreshold\0\0thresholdL\0"
    "thresholdLChanged(double)\0thresholdH\0"
    "thresholdHChanged(double)\0ch\0"
    "channelChanged(int)\0"
};

void SigParamWithDualThreshold::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        SigParamWithDualThreshold *_t = static_cast<SigParamWithDualThreshold *>(_o);
        switch (_id) {
        case 0: _t->thresholdLChanged((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 1: _t->thresholdHChanged((*reinterpret_cast< double(*)>(_a[1]))); break;
        case 2: _t->channelChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData SigParamWithDualThreshold::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject SigParamWithDualThreshold::staticMetaObject = {
    { &SigParamSelectionDialog::staticMetaObject, qt_meta_stringdata_SigParamWithDualThreshold,
      qt_meta_data_SigParamWithDualThreshold, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &SigParamWithDualThreshold::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *SigParamWithDualThreshold::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *SigParamWithDualThreshold::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_SigParamWithDualThreshold))
        return static_cast<void*>(const_cast< SigParamWithDualThreshold*>(this));
    return SigParamSelectionDialog::qt_metacast(_clname);
}

int SigParamWithDualThreshold::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = SigParamSelectionDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 3)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 3;
    }
    return _id;
}
static const uint qt_meta_data_SigParamAmplitudeDialog[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       1,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      35,   25,   24,   24, 0x08,

       0        // eod
};

static const char qt_meta_stringdata_SigParamAmplitudeDialog[] = {
    "SigParamAmplitudeDialog\0\0threshold\0"
    "thresholdChanged(double)\0"
};

void SigParamAmplitudeDialog::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        SigParamAmplitudeDialog *_t = static_cast<SigParamAmplitudeDialog *>(_o);
        switch (_id) {
        case 0: _t->thresholdChanged((*reinterpret_cast< double(*)>(_a[1]))); break;
        default: ;
        }
    }
}

const QMetaObjectExtraData SigParamAmplitudeDialog::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject SigParamAmplitudeDialog::staticMetaObject = {
    { &SigParamWithDualThreshold::staticMetaObject, qt_meta_stringdata_SigParamAmplitudeDialog,
      qt_meta_data_SigParamAmplitudeDialog, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &SigParamAmplitudeDialog::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *SigParamAmplitudeDialog::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *SigParamAmplitudeDialog::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_SigParamAmplitudeDialog))
        return static_cast<void*>(const_cast< SigParamAmplitudeDialog*>(this));
    return SigParamWithDualThreshold::qt_metacast(_clname);
}

int SigParamAmplitudeDialog::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = SigParamWithDualThreshold::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 1)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 1;
    }
    return _id;
}
static const uint qt_meta_data_SigParamSaturationDialog[] = {

 // content:
       6,       // revision
       0,       // classname
       0,    0, // classinfo
       2,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: signature, parameters, type, tag, flags
      26,   25,   25,   25, 0x09,
      47,   25,   25,   25, 0x09,

       0        // eod
};

static const char qt_meta_stringdata_SigParamSaturationDialog[] = {
    "SigParamSaturationDialog\0\0"
    "on_btnLeft_clicked()\0on_btnRight_clicked()\0"
};

void SigParamSaturationDialog::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        Q_ASSERT(staticMetaObject.cast(_o));
        SigParamSaturationDialog *_t = static_cast<SigParamSaturationDialog *>(_o);
        switch (_id) {
        case 0: _t->on_btnLeft_clicked(); break;
        case 1: _t->on_btnRight_clicked(); break;
        default: ;
        }
    }
    Q_UNUSED(_a);
}

const QMetaObjectExtraData SigParamSaturationDialog::staticMetaObjectExtraData = {
    0,  qt_static_metacall 
};

const QMetaObject SigParamSaturationDialog::staticMetaObject = {
    { &SigParamWithDualThreshold::staticMetaObject, qt_meta_stringdata_SigParamSaturationDialog,
      qt_meta_data_SigParamSaturationDialog, &staticMetaObjectExtraData }
};

#ifdef Q_NO_DATA_RELOCATION
const QMetaObject &SigParamSaturationDialog::getStaticMetaObject() { return staticMetaObject; }
#endif //Q_NO_DATA_RELOCATION

const QMetaObject *SigParamSaturationDialog::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->metaObject : &staticMetaObject;
}

void *SigParamSaturationDialog::qt_metacast(const char *_clname)
{
    if (!_clname) return 0;
    if (!strcmp(_clname, qt_meta_stringdata_SigParamSaturationDialog))
        return static_cast<void*>(const_cast< SigParamSaturationDialog*>(this));
    return SigParamWithDualThreshold::qt_metacast(_clname);
}

int SigParamSaturationDialog::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = SigParamWithDualThreshold::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 2)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 2;
    }
    return _id;
}
QT_END_MOC_NAMESPACE
