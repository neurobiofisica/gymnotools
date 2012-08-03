#ifndef SVMUTIL_H
#define SVMUTIL_H

#include "svm/svm.h"

class SVMNodeList
{
    svm_node *nodes;
    int size;

public:
    /**
     * Constructs a SVM node list
     * @param samples number of samples to hold
     */
    explicit SVMNodeList(int samples)
    {
        nodes = new svm_node[samples+1];
        for(int i = 0; i < samples; i++)
            nodes[i].index = i + 1;
        nodes[samples].index = -1;
        size = samples;
    }

    ~SVMNodeList()
    {
        delete[] nodes;
    }

    /**
     * Fill the node list using the contents of a buffer
     * @param buf the buffer
     */
    void fill(float *buf)
    {
        for(int i = 0; i < size; i++)
            nodes[i].value = buf[i];
    }

    /**
     * Retrieves the SVM node list
     */
    operator svm_node *() const { return nodes; }
};

#endif // SVMUTIL_H
