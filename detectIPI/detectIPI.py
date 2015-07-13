import sys, os
import numpy as np

sys.path.append( os.path.realpath('../python/') )
sys.path.append( os.path.realpath('../') )
import recogdb

NumChannels = 11 #importar isso do arquivo C?

def usage():
    print "Usage: python DetectIPIs.py filename.db outfile.ipi"
    sys.exit(-1)


if len(sys.argv) != 3:
    usage()

if not os.path.isfile(sys.argv[1]):
    usage()

db = recogdb.openDB(sys.argv[1],'w')
f = open(sys.argv[2],'w')

# Variables for each fish
SpikesLidos = { 'A':0, 
                'B':0,
              }
Derivada = {    'A':None,
                'B':None,
           }
NPontosJanela = {   'A': 0,
                    'B': 0,
                }
NPontosJanelaAnterior = { 'A': 0,
                            'B': 0,
                          }
MediaCentro = { 'A':0,
                'B':0,
              }
flag = {    'A': 1,
            'B': -1,
       }
prob = {    'A': 0.,
            'B': 0.,
       }
allOffs = {}
OffsRaw = {}

print 'enter DB'
for rec in db.iteritems():
    # Gambi pra verificar se o spike ja foi classificado
    off, bindata = rec
    read_data = recogdb.parseDBHeader(bindata)
    correctedPosA = read_data[ recogdb.dicFields['correctedPosA'] ]
    correctedPosB = read_data[ recogdb.dicFields['correctedPosB'] ]

    if (correctedPosA != -1) and (correctedPosB != -1):
        f.write( '%d\t%d\n'%(1, correctedPosA) )
        f.write( '%d\t%d\n'%(-1, correctedPosB) )
        continue
    if (correctedPosA != -1):
        f.write( '%d\t%d\n'%(1, correctedPosA) )
        continue
    elif (correctedPosB != -1):
        f.write( '%d\t%d\n'%(-1, correctedPosB) )
        continue

    offraw, direction, distA, distB, distAB, SaturationFlag, svm, pairsvm, prob['A'], prob['B'], fishwins = recogdb.fishrec(rec)
    off = offraw/4/NumChannels

    if SaturationFlag == 2**NumChannels - 1:
        print "All channels saturated!"
        for PIdx in fishwins.keys():
            print str(PIdx) + ' ' + str(SpikesLidos[PIdx]+1)
        print ' '
    CanaisSat = [(SaturationFlag & (1<<ch)) != 0 for ch in xrange(NumChannels)]

    flagBoth = False
    if ('A' in fishwins) and ('B' in fishwins):
        flagBoth = True

    for PIdx in fishwins.keys():

        offset = fishwins[PIdx][0]
        NPontosJanelaAnterior[PIdx] = NPontosJanela[PIdx]
        NPontosJanela[PIdx] = fishwins[PIdx][1][0].size

        SpikesLidos[PIdx] = SpikesLidos[PIdx] + 1

        if flagBoth == True:
            MediaCentro[PIdx] = MediaCentro[PIdx] - ( NPontosJanelaAnterior[PIdx] - NPontosJanela[PIdx] )

        else:
            #assert offset == 0

            Maximos = np.zeros(NumChannels)
            IdxMaximos = np.zeros(NumChannels)
            for i in xrange(NumChannels):
                if CanaisSat[i] == True:
                    continue

                Derivada[PIdx] = np.abs(np.diff(fishwins[PIdx][1][i]))
                if Derivada[PIdx].size == 0:
                    print 'ERROR: Zero sized derivative'
                
                IdxMaximos[i] = Derivada[PIdx].argmax()
                Maximos[i] = Derivada[PIdx][ IdxMaximos[i] ]

            MediaCentro[PIdx] = np.dot(IdxMaximos,Maximos) / sum(Maximos)

        out = int(round(off + offset + MediaCentro[PIdx]))
        allOffs[offraw] = out
        OffsRaw[out] = offraw

        assert ( (flag[PIdx] == 1) or (flag[PIdx] == -1) )

        f.write( '%d\t%d\n'%(flag[PIdx],out) )
        if flag[PIdx] == 1:
            recogdb.updateHeaderEntry(db, offraw, 'correctedPosA', out, change_svm=False, sync=False)
        else:
            recogdb.updateHeaderEntry(db, offraw, 'correctedPosB', out, change_svm=False, sync=False)

db.sync()

f.close()
db.close()
