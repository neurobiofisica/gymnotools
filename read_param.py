import re,os

sigcfg = open( os.path.join(os.path.dirname(__file__), 'common/sigcfg.h'), 'r')

for l in sigcfg.readlines():
    if len( re.findall(r'static const int NumChannels',l)) > 0:
        NChan = int( l.split('=')[1].strip().strip(';') )
    if len( re.findall(r'static const double SamplingRate',l)) > 0:
        freq = float( l.split('=')[1].strip().strip(';') )
    if len( re.findall(r'static const int EODSamples', l)) > 0:
        winSize = int( l.split('=')[1].strip().strip(';') )
