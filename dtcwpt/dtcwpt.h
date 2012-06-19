/* Dual Tree Complex Wavelet Packet Transform */

/*
 * Copyright (c) 2010-2011 Paulo Matias
 *
 * Permission to use, copy, modify, and distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#ifndef DTCWPT_H
#define DTCWPT_H

#include "wfb.h"

typedef struct {
    wavelet_filt *first;  /* First stage filters */
    wavelet_filt *cwt;    /* CWT-specific filters (e.g. q-shift filters) */
    wavelet_filt *f;      /* Filters for branches already satisfying Hilbert conditions */ 
} cwpt_filt;

void cwpt_fulltree(cwpt_filt *filt, float *in, unsigned int n, float *out);
void dtcwpt_mix(float *tree1, float *tree2, unsigned int n, float *out);
void invcwpt_level(cwpt_filt *filt, float *in, unsigned int n, unsigned int level, float *out);

typedef struct {
    wavelet_filt *filt;
    unsigned int in_off, n, hout_off, gout_off;
} prepared_cwpt_stmt;

typedef struct {
    int level, node;
} cwpt_stop_point;

typedef struct {
    unsigned int n, nps, numstmts, size;
    cwpt_filt *filt;
    cwpt_stop_point *ps;
    prepared_cwpt_stmt *stmts;
} prepared_cwpt;

prepared_cwpt *cwpt_prepare(cwpt_filt *filt, unsigned int n, cwpt_stop_point *ps, unsigned int nps);
void cwpt_exec(prepared_cwpt *cwpt, float *in, float *tmp);
void invcwpt_exec(prepared_cwpt *cwpt, float *in, float *tmp);
void cwpt_free(prepared_cwpt *cwpt);

void cwpt_tree_select(float *in, float *out, unsigned int n, cwpt_stop_point *ps, unsigned int nps);

typedef double(*bestbasis_cb_t)(void *arg, int level, unsigned int off, unsigned int n);
typedef enum {
    BESTBASIS_MIN,
    BESTBASIS_MAX
} bestbasis_optim_t;

cwpt_stop_point *bestbasis_find(bestbasis_cb_t cb, void *arg, bestbasis_optim_t optim, unsigned int n, unsigned int *nps);

#endif
