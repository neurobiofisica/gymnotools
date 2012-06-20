#ifndef RESIZABLEBUFFER_H
#define RESIZABLEBUFFER_H

/**
 * Destructive resizable buffer.
 * Warning: Resizing the buffer causes destruction of its contents.
 */
class ResizableBuffer
{
public:
    explicit ResizableBuffer(int size = 1024) { newbuffer(size); }
    ~ResizableBuffer() { delete [] buffer; }
    /**
     * Get a pointer to the buffer
     * @returns the pointer
     */
    float *buf() const { return buffer; }
    /**
     * Reserve space in the buffer, destructing any previous contents
     * @param size requested size for the buffer
     */
    void reserve(int size) {
        if(size > cursize) {
            delete [] buffer;
            newbuffer(size);
        }
    }
private:
    void newbuffer(int size) {
        buffer = new float[size];
        cursize = size;
    }
    float *buffer;
    int cursize;
};

#endif // RESIZABLEBUFFER_H
