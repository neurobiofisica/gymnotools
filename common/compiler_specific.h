#ifndef COMPILER_SPECIFIC_H
#define COMPILER_SPECIFIC_H

#ifdef __cplusplus
extern "C"
{
#endif

#ifdef __GNUC__

#define ALIGN(n)    __attribute__((aligned(n)))
#define INLINE      inline
#define AINLINE     inline __attribute__((always_inline))
#define RESTRICT    __restrict__

#define LIKELY(x)   __builtin_expect(!!(x), 1)
#define UNLIKELY(x) __builtin_expect(!!(x), 0)

typedef float __attribute__((aligned(16))) afloat;

#else

#define ALIGN(n)
#define INLINE
#define AINLINE
#define LIKELY(x) (x)
#define UNLIKELY(x) (x)

typedef float afloat;

#endif

#ifdef __cplusplus
}
#endif

#endif // COMPILER_SPECIFIC_H
