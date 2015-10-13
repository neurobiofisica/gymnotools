#ifndef SVMUTIL_H
#define SVMUTIL_H

#include "svm/svm.h"

class SVMNodeList
{
    svm_node node;

public:
    /**
     * Constructs a SVM node list
     * @param samples number of samples to hold
     */
    explicit SVMNodeList(int samples)
    {
        node.dim = samples;
        node.values = new double[samples];
    }

    ~SVMNodeList()
    {
        delete[] node.values;
    }

    /**
     * Fill the node list using the contents of a buffer
     * @param buf the buffer
     */
    void fill(float *buf)
    {
        for(int i = 0; i < node.dim; i++)
            node.values[i] = buf[i];
    }

    /**
     * Retrieves the SVM node list
     */
    operator svm_node *() { return &node; }
};

#endif // SVMUTIL_H
