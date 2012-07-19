#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "dSFMT.h"
#include "entropy.h"

#if defined(__linux__)

void dsfmt_gv_init_with_entropy() {
    uint32_t seed[4];
    FILE *f = NULL;
    f = fopen("/dev/urandom", "rb");
    if(f == NULL)
        goto fallback;
    if(fread(&seed, sizeof(seed), 1, f) != 1)
        goto fallback;
    dsfmt_gv_init_by_array(seed, sizeof(seed)/sizeof(uint32_t));
    fclose(f);
    return;
fallback:;
    if(f != NULL)
        fclose(f);
    dsfmt_gv_init_gen_rand(time(NULL));
}

#else

void dsfmt_gv_init_with_entropy() {
    dsfmt_gv_init_gen_rand(time(NULL));
}

#endif
