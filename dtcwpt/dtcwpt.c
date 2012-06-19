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

/* For reference, see the paper:
 * On the Dual-Tree Complex Wavelet Packet and M-Band Transforms
 * Ilker Bayram, Student Member, IEEE, and Ivan W. Selesnick, Member, IEEE
 * IEEE Transactions on Signal Processing, 2008.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <assert.h>

#include "wfb.h"
#include "dtcwpt.h"

/* Computes a full CWPT tree
 * filt: CWPT filters
 * in: input vector
 * n: size of the input vector (n >= 2^2)
 * out: output vector (size: [log2(n)+1]*n)
 */
void cwpt_fulltree(cwpt_filt *filt, float *in, unsigned int n, float *out) {
    unsigned int n2 = n >> 1;
    unsigned int m = n2, i, j, off;

    /* Copy unmodified signal to the first node of the tree */
    memcpy(out, in, n*sizeof(float));

    /* First stage */
    afb(filt->first, &out[0], n, &out[n], &out[n+m]);

    /* Second stage */
    off = n<<1;
    afb(filt->cwt, &out[n  ], m, &out[off         ], &out[off+(m>>1)]);
    afb(filt->cwt, &out[n+m], m, &out[off+m+(m>>1)], &out[off+ m    ]);

    /* Next stages */
    for(m >>= 1; m > 1; m >>= 1) {
        /* Process each node */
        for(i=0,j=0; i<n; i+=m,off+=m,j++) {
            /* Choose the adequate filter pair */
            wavelet_filt *wf = (i==0 || i==n2) ? filt->cwt : filt->f;
            /* Swap the outputs if the parent node was the result of a
             * high-pass filtering.
             */
            int m2 = m >> 1;
            float *hout = (j&1)==0 ? &out[off+n   ] : &out[off+n+m2];
            float *gout = (j&1)==0 ? &out[off+n+m2] : &out[off+n   ];
            /* Filter and store in two children nodes */
            afb(wf, &out[off], m, hout, gout);
        }
    }
}

/* Mix two CWPT trees to compute an approximately shift-invariant DT-CWPT
 * tree1, tree2: CWPT trees
 * n: size of each CWPT tree
 * out: output vector (size: n, may be the same as tree1 or tree2)
 */
void dtcwpt_mix(float *tree1, float *tree2, unsigned int n, float *out) {
    unsigned int i;
    for(i = 0; i < n; i++) {
        float a1 = tree1[i];
        float a2 = tree2[i];
        out[i] = sqrt(.5*(a1*a1 + a2*a2));
    }
}

/* Inverts the given level of a CWPT
 * filt: CWPT filters
 * in: input vector
 * n: size of the input vector (n >= 2^2)
 * level: transform level of the input vector (level > 0)
 * out: output vector (size: n)
 */
void invcwpt_level(cwpt_filt *filt, float *in, unsigned int n, unsigned int level, float *out) {
    unsigned int n2 = n >> 1;
    unsigned int m, i, j;
    unsigned int vecsize = n*sizeof(float);
    float *tmp;

    assert((tmp = malloc(vecsize)) != NULL);
    memcpy(tmp, in, vecsize);

    /* Initial m for the level stage */
    for(m = n, i = 0; i < level-1; i++)
        m >>= 1;

    /* Last to third stages */
    for(; level > 2; m <<= 1, level--) {
        /* Process each node */
        for(i=0,j=0; i<n; i+=m,j++) {
            /* Choose the adequate filter pair */
            wavelet_filt *wf = (i==0 || i==n2) ? filt->cwt : filt->f;
            /* Swap the inputs if the parent node is the result of a
             * high-pass filtering.
             */
            int m2 = m >> 1;
            float *hin = (j&1)==0 ? &tmp[i   ] : &tmp[i+m2];
            float *gin = (j&1)==0 ? &tmp[i+m2] : &tmp[i   ];
            /* Filter and store in the parent node */
            sfb(wf, hin, gin, m, &out[i]);
        }
        memcpy(tmp, out, vecsize);
    }

    m = n2;

    /* Second stage */
    if(level == 2) {
        sfb(filt->cwt, &tmp[0       ], &tmp[m>>1], m, &out[0]);
        sfb(filt->cwt, &tmp[m+(m>>1)], &tmp[m   ], m, &out[m]);
        memcpy(tmp, out, vecsize);
        level--;
    }

    /* First stage */
    if(level == 1) {
        sfb(filt->first, &tmp[0], &tmp[m], n, &out[0]);
    }

    free(tmp);
}

/* Recursive function to prepare a transform */
static void _prep(prepared_cwpt *cwpt, unsigned int n, int level, int node) {
    unsigned int i;
    prepared_cwpt_stmt *stmt;
    /* check if this is a stop point */
    assert(cwpt->nps != 0);
    if(cwpt->ps->level == level && cwpt->ps->node == node) {
        cwpt->nps--;
        cwpt->ps++;
        return;
    }
    assert(n > 1);
    /* alloc space if needed */
    if(cwpt->numstmts >= cwpt->size) {
        cwpt->size <<= 1;
        assert((cwpt->stmts = realloc(cwpt->stmts, cwpt->size*sizeof(prepared_cwpt_stmt))) != NULL);
    }
    stmt = &cwpt->stmts[cwpt->numstmts++];
    stmt->n = n;
    /* First stage */
    if(level == 0) {
        stmt->filt = cwpt->filt->first;
        stmt->in_off = 0;
        stmt->hout_off = 0;
        stmt->gout_off = n>>1;
    }
    /* Second stage */
    else if(level == 1) {
        stmt->filt = cwpt->filt->cwt;
        if(node == 0) {
            stmt->in_off = 0;
            stmt->hout_off = 0;
            stmt->gout_off = n>>1;
        }
        else {
            stmt->in_off = n;
            stmt->hout_off = n + (n>>1);
            stmt->gout_off = n;
        }
    }
    /* Next stages */
    else {
        int n2 = cwpt->n >> 1;
        int m2 = n >> 1;
        i  = node * n;
        stmt->filt = (i==0 || i==n2) ? cwpt->filt->cwt : cwpt->filt->f;
        stmt->in_off = i;
        stmt->hout_off = (node&1)==0 ? i    : i+m2;
        stmt->gout_off = (node&1)==0 ? i+m2 : i   ;
    }
    /* Walk over childs */
    _prep(cwpt, n>>1, level+1, (node<<1)  );
    _prep(cwpt, n>>1, level+1, (node<<1)|1);
}

/* Callback to compare two stop points for sorting */
static int _prep_sort(const void *a1, const void *a2) {
    const cwpt_stop_point *p1 = a1, *p2 = a2;
    int diff =  (p1->node << p2->level) - (p2->node << p1->level);
    if(diff != 0)
        return diff;
    return p1->level - p2->level;
}

/* Prepare a CWPT
 * filt: CWPT filters
 * n: size of the input vector
 * ps: stop points (last level nodes, may be modified for sorting)
 */
prepared_cwpt *cwpt_prepare(cwpt_filt *filt, unsigned int n, cwpt_stop_point *ps, unsigned int nps) {
    prepared_cwpt *cwpt;
    assert((cwpt = malloc(sizeof(prepared_cwpt))) != NULL);
    cwpt->size = n;  /* initial number of allocated entries */
    cwpt->n = n;
    cwpt->numstmts = 0;
    cwpt->filt = filt;
    assert((cwpt->stmts = malloc(cwpt->size*sizeof(prepared_cwpt_stmt))) != NULL);
    qsort(ps, nps, sizeof(cwpt_stop_point), _prep_sort);
    cwpt->ps = ps;
    cwpt->nps = nps;
    _prep(cwpt, n, 0, 0);
    cwpt->size = cwpt->n;
    assert((cwpt->stmts = realloc(cwpt->stmts, cwpt->size*sizeof(prepared_cwpt_stmt))) != NULL);
    return cwpt;
}

/* Computes a prepared CWPT
 * cwpt: prepared packet transform
 * in: input/output vector
 * tmp: temporary vector (same size as in)
 */
void cwpt_exec(prepared_cwpt *cwpt, float *in, float *tmp) {
    int i;
    for(i = 0; i < cwpt->numstmts; i++) {
        prepared_cwpt_stmt *stmt = &cwpt->stmts[i];
        unsigned int size = stmt->n*sizeof(float);
        afb(stmt->filt, &in[stmt->in_off], stmt->n, &tmp[stmt->hout_off], &tmp[stmt->gout_off]);
        memcpy(&in[stmt->in_off], &tmp[stmt->in_off], size);
    }
}

/* Computes the inverse of a prepared CWPT
 * cwpt: prepared packet transform
 * in: input/output vector
 * tmp: temporary vector (same size as in)
 */
void invcwpt_exec(prepared_cwpt *cwpt, float *in, float *tmp) {
    int i;
    for(i = cwpt->numstmts-1; i >= 0; i--) {
        prepared_cwpt_stmt *stmt = &cwpt->stmts[i];
        unsigned int size = stmt->n*sizeof(float);
        sfb(stmt->filt, &in[stmt->hout_off], &in[stmt->gout_off], stmt->n, &tmp[stmt->in_off]);
        memcpy(&in[stmt->in_off], &tmp[stmt->in_off], size);
    }
}

/* Free a prepared CWPT
 * cwpt: prepared packet transform
 */
void cwpt_free(prepared_cwpt *cwpt) {
    free(cwpt->stmts);
    free(cwpt);
}

/* Select elements from a full tree acording to a list of stop points.
 * in: full tree (size: [1+log(n)]*n)
 * out: output vector (size: n)
 * n: size of the output vector
 * ps: stop point list
 * nps: number of stop points
 */
void cwpt_tree_select(float *in, float *out, unsigned int n, cwpt_stop_point *ps, unsigned int nps) {
    unsigned int i, m, maxlevel=0;
    /* Count number of levels */
    for(m = n; m > 1; m >>= 1)
        maxlevel++;
    /* Copy data */
    for(i = 0; i < nps; i++) {
        cwpt_stop_point *p = &ps[i];
        unsigned int lev  = maxlevel - p->level;
        unsigned int off1 = p->node << lev;
        unsigned int off2 = p->level * n;
        unsigned int len  = 1 << lev;
        memcpy(&out[off1], &in[off1+off2], len*sizeof(float));
    }
}

/* Finds the best basis in a full tree by calling the callback to get a metric
 * cb: callback
 * n: size of the transform
 */
cwpt_stop_point *bestbasis_find(bestbasis_cb_t cb, void *arg, bestbasis_optim_t optim, unsigned int n, unsigned int *nps_) {
    unsigned int m, off, off2, nps;
    int level, maxlevel = 0;
    cwpt_stop_point *ps;
    double *ametric;
    int *alen, *alev;
    /* Alloc temp stuff */
    assert((ametric = malloc(n*sizeof(double)))!=NULL);
    assert((alen = malloc(n*sizeof(int)))!=NULL);
    assert((alev = malloc(n*sizeof(int)))!=NULL);
    /* Count number of levels */
    for(m = n; m > 1; m >>= 1)
        maxlevel++;
    /* Last level */
    for(off = 0; off < n; off++) {
        double nodemetric = cb(arg, maxlevel, off, 1);
        ametric[off] = nodemetric;
        alen[off] = 1;
        alev[off] = maxlevel;
    }
    /* Previous levels */
    for(m=2,level=maxlevel-1; level>=0; m<<=1,level--) {
        for(off = 0; off < n; off+=m) {
            double newm = cb(arg, level, off, m);
            double curm = 0.;
            for(off2 = 0; off2 < m; off2 += alen[off+off2])
                curm += ametric[off+off2];
            if(optim == BESTBASIS_MAX ? (newm >= curm) : (newm <= curm)) {
                ametric[off] = newm;
                alen[off] = m;
                alev[off] = level;
            }
        }
    }
    /* Count number of stop points and alloc */
    for(nps=0,off=0; off<n; off+=alen[off],nps++);
    assert((ps = malloc(nps*sizeof(cwpt_stop_point)))!=NULL);
    *nps_ = nps;
    /* Convert into a stop point list */
    for(nps=0,off=0; off<n; off+=alen[off],nps++) {
        cwpt_stop_point *p = &ps[nps];
        p->level = alev[off];
        p->node = off / alen[off];
    }
    /* Free unused data */
    free(alev);
    free(alen);
    free(ametric);
    return ps;
}
