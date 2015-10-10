import ctypes
lib = ctypes.CDLL('./libexportSym.so')

NumChannels = ctypes.cast( lib.NumChannels, ctypes.POINTER(ctypes.c_int) ).contents.value
SamplingRate = ctypes.cast( lib.SamplingRate, ctypes.POINTER(ctypes.c_double) ).contents.value
EODSamples = ctypes.cast( lib.EODSamples, ctypes.POINTER(ctypes.c_int) ).contents.value

BytesPerSample = ctypes.cast( lib.BytesPerSample, ctypes.POINTER(ctypes.c_int) ).contents.value


defaultLowpassNumTaps = ctypes.cast( lib.defaultLowpassNumTaps, ctypes.POINTER(ctypes.c_int) ).contents.value
defaultLowPassCutoff = ctypes.cast( lib.defaultLowPassCutoff, ctypes.POINTER(ctypes.c_float) ).contents.value
defaultDetectionThreshold = ctypes.cast( lib.defaultDetectionThreshold, ctypes.POINTER(ctypes.c_float) ).contents.value
defaultMinLevel = ctypes.cast( lib.defaultMinLevel, ctypes.POINTER(ctypes.c_float) ).contents.value
defaultMinRatio = ctypes.cast( lib.defaultMinRatio, ctypes.POINTER(ctypes.c_float) ).contents.value
defaultStopSamples = ctypes.cast( lib.defaultStopSamples, ctypes.POINTER(ctypes.c_int) ).contents.value
defaultOnlyAbove = ctypes.cast( lib.defaultOnlyAbove, ctypes.POINTER(ctypes.c_float) ).contents.value
defaultSaturationLow = ctypes.cast( lib.defaultSaturationLow, ctypes.POINTER(ctypes.c_float) ).contents.value
defaultSaturationHigh = ctypes.cast( lib.defaultSaturationHigh, ctypes.POINTER(ctypes.c_float) ).contents.value

defaultStormGlue = ctypes.cast( lib.defaultStormGlue, ctypes.POINTER(ctypes.c_int) ).contents.value
defaultStormSize = ctypes.cast( lib.defaultStormSize, ctypes.POINTER(ctypes.c_int) ).contents.value
defaultStormAfterGlue = ctypes.cast( lib.defaultSaturationHigh, ctypes.POINTER(ctypes.c_int) ).contents.value

defaultSingleMinWins = ctypes.cast( lib.defaultSingleMinWins, ctypes.POINTER(ctypes.c_int) ).contents.value
defaultSingleMinProb = ctypes.cast( lib.defaultSingleMinProb, ctypes.POINTER(ctypes.c_float) ).contents.value
defaultSingleMaxDist = ctypes.cast( lib.defaultSingleMaxDist, ctypes.POINTER(ctypes.c_int) ).contents.value

defaultRecogFillSamples = ctypes.cast( lib.defaultRecogFillSamples, ctypes.POINTER(ctypes.c_int) ).contents.value
