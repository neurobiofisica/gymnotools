%module pygymnext
%{
#define SWIG_FILE_WITH_INIT
#include "common/featureutil.h"

#define IN_SIZE EODSamples
#define OUT_SIZE (NumFFTFeatures+NumDTCWPTFeatures)
%}

%include "numpy.i"

%init %{
    import_array();
%}

%apply (float INPLACE_ARRAY1[ANY]) {(float arrin[IN_SIZE])};
%apply (float INPLACE_ARRAY1[ANY]) {(float arrout[OUT_SIZE])};

class FeatureProcessor {
public:
    FeatureProcessor(float arrin[IN_SIZE], float arrout[OUT_SIZE]);
    ~FeatureProcessor();
    void process();
};

