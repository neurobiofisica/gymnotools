/* Dual Tree Complex Wavelet Packet Transform */

/*
 * Copyright (c) 2010-2012 Paulo Matias
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

/**
 * Computes a full CWPT tree
 * @param filt CWPT filters
 * @param in input vector
 * @param n size of the input vector (n >= 2^2)
 * @param out output vector (size: [log2(n)+1]*n)
 */
void cwpt_fulltree(const cwpt_filt *filt, const float *in, unsigned int n, float *out);

/**
 * Mix two CWPT trees to compute an approximately shift-invariant DT-CWPT
 * @param tree1 CWPT tree
 * @param tree2 CWPT tree
 * @param n size of each CWPT tree
 * @param out output vector (size: n, may be the same as tree1 or tree2)
 */
void dtcwpt_mix(const float *tree1, const float *tree2, unsigned int n, float *out);

/**
 * Inverts the given level of a CWPT
 * @param filt CWPT filters
 * @param in input vector
 * @param n size of the input vector (n >= 2^2)
 * @param level transform level of the input vector (level > 0)
 * @param out output vector (size: n)
 */
void invcwpt_level(const cwpt_filt *filt, const float *in, unsigned int n, unsigned int level, float *out);

typedef struct {
    wavelet_filt *filt;
    unsigned int in_off, n, hout_off, gout_off;
} prepared_cwpt_stmt;

typedef struct {
    int level, node;
} cwpt_stop_point;

typedef struct {
    unsigned int n, nps, numstmts, size;
    const cwpt_filt *filt;
    cwpt_stop_point *ps;
    prepared_cwpt_stmt *stmts;
} prepared_cwpt;

/**
 * Prepare a CWPT
 * @param filt CWPT filters
 * @param n size of the input vector
 * @param ps stop points (last level nodes, may be modified for sorting)
 * @returns a prepared packet transform
 */
prepared_cwpt *cwpt_prepare(const cwpt_filt *filt, unsigned int n, cwpt_stop_point *ps, unsigned int nps);

/**
 * Computes a prepared CWPT
 * @param cwpt prepared packet transform
 * @param in input/output vector
 * @param tmp temporary vector (same size as in)
 */
void cwpt_exec(const prepared_cwpt *cwpt, float *in, float *tmp);

/**
 * Computes the inverse of a prepared CWPT
 * @param cwpt prepared packet transform
 * @param in input/output vector
 * @param tmp temporary vector (same size as in)
 */
void invcwpt_exec(const prepared_cwpt *cwpt, float *in, float *tmp);

/**
 * Free a prepared CWPT
 * @param cwpt prepared packet transform
 */
void cwpt_free(prepared_cwpt *cwpt);

/**
 * Select elements from a full tree acording to a list of stop points.
 * @param in full tree (size: [1+log(n)]*n)
 * @param out output vector (size: n)
 * @param n size of the output vector
 * @param ps stop point list
 * @param nps number of stop points
 */
void cwpt_tree_select(const float *in, float *out, unsigned int n, const cwpt_stop_point *ps, unsigned int nps);

typedef double(*bestbasis_cb_t)(void *arg, int level, unsigned int off, unsigned int n);
typedef enum {
    BESTBASIS_MIN,
    BESTBASIS_MAX
} bestbasis_optim_t;

/**
 * Finds the best basis in a full tree by calling the callback to get a measure
 * @param cb callback
 * @param arg first argument passed to the callback
 * @param optim chooses whether the measure will be maximized or minimized
 * @param n size of the transform
 * @param nps_ pointer to an integer which will hold the number of stop points
 * @returns pointer to a list of stop points
 */
cwpt_stop_point *bestbasis_find(bestbasis_cb_t cb, void *arg, bestbasis_optim_t optim, unsigned int n, unsigned int *nps);

#endif
