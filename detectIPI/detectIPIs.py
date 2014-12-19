import bsddb3, sys, os
import recogdb # Lembrar de colocar essa biblioteca junto
import numpy as np

amostra = 24557
Peixe = 'A'


NumChannels = 11 #importar isso do arquivo C?

def usage():
    print "Usage: python DetectIPIs.py filename.db outfile.ipi"
    sys.exit(-1)


if len(sys.argv) != 3:
    usage()

if not os.path.isfile(sys.argv[1]):
    usage()

print sys.argv[1]
db = bsddb3.btopen(sys.argv[1],'r')
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

for rec in db.iteritems():
    off, distA, distB, distAB, SaturationFlag, fishwins = recogdb.fishrec(rec)
    off = off/4/NumChannels

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
        f.write(str(flag[PIdx]) + '\t' + str(int(round(off + offset + MediaCentro[PIdx]))) + '\n' )

f.close()
db.close()
