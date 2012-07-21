#ifndef STATIC_LOG2_H
#define STATIC_LOG2_H

template<int n> struct static_log2 {
    enum { value = 1 + static_log2<n/2>::value };
};

template<> struct static_log2<1> {
    enum { value = 0 };
};

#endif // STATIC_LOG2_H
