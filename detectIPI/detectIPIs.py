import bsddb3, sys, os
import recogdb # Lembrar de colocar essa biblioteca junto
import numpy as np

amostra = 24557
Peixe = 'A'


NumChannels = 11 #importar isso do arquivo C?

def usage():
    print "Usage: python DetectIPIs.py filename.db outfile.ipi"
    sys.exit(-1)


if len(sys.argv) != 4:
    usage()

if not os.path.isfile(sys.argv[1]):
    usage()

print sys.argv[1]
db = bsddb3.btopen(sys.argv[1],'r')
f = open(sys.argv[2],'w')
f2 = open(sys.argv[3], 'w')

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

for rec in db.iteritems():
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

        pair = 0
        if svm == 's':
            pair = allOffs[pairsvm]

        f.write( '%d\t%d\n'%(flag[PIdx],out) )
        f2.write( '%d\t%d\t%d\t%d\t%c\t%d\t%f\t%f\t%f\t%f\t%f\n'%(flag[PIdx],out,offraw,direction,svm,pair,prob['A'], prob['B'], distA, distB, distAB ) )

f.close()
f2.close()
db.close()
