#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import recogdb
import struct

import sys

if sys.version_info.major == 3:
    xrange = range
    mode = 'b'
else:
    mode = ''

direction = -1
NChan = 11
freq = 45454.545454
overlapRange = int(0.002*freq)

foda = False

# Verificar se lastLen esta em bytes
class winFile:
    def __init__(self, f):
        self.f = f
        self.lastLen, self.off, self.samples, self.channels, self.sigs, self.center = self.readWin()
        self.nowLen = (4+8+4+4+4) + self.channels*4*(1 + self.samples)
        self.f.seek(0)
        self.beg = True

    def readWin(self):
        raw = self.f.read(4+8+4+4+4)
        if raw == '':
            return None
        try: ##############################################################
            lastLen, off, samples, channels, center = struct.unpack('=iqiii', raw)
        except struct.error:
            return None
        sigs = {}
        for ch in range(channels):
            chid, = struct.unpack('i', self.f.read(4))
            win = np.frombuffer(self.f.read(samples*4), dtype=np.float32)
            sigs.update( {chid: win} )
        return lastLen, off, samples, channels, center, sigs

    def nextWin(self):
        self.beg = False
        ret = self.readWin()
        if ret == None:
            return None
        self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs = ret
        self.nowLen = (4+8+4+4+4) + self.channels*4*(1 + self.samples)
        return self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs

    def prevWin(self):
        if self.beg == True:
            return None
        self.f.seek(self.f.tell() - self.lastLen)
        self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs = self.readWin()
        self.nowLen = (4+8+4+4+4) + self.channels*4*(1 + self.samples)
        self.f.seek(self.f.tell() - self.nowLen)
        if self.f.tell() == 0:
            self.beg = True
        return self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs

    def beg(self):
        self.f.seek(0)
        self.lastLen, self.off, self.samples, self.channels, self.center, self.sigs = self.readWin()
        self.nowLen = (4+8+4+4+4) + self.channels*4*(1 + self.samples)
        self.f.seek(0)
        self.beg = True

    def end(self):
        while self.nextWin() != None:
            pass
        self.beg = False



db = recogdb.openDB(sys.argv[2], 'w')
wins = winFile(open(sys.argv[3], mode+'r'))
svmpairs = np.loadtxt(sys.argv[4], dtype=np.int64)
svmpairsTam = svmpairs.shape[0]

probsfile = open(sys.argv[5], 'r')
probs = {}
for l in probsfile.readlines():
    #cause, offstr, pairstr, probAstr, probBstr = l.strip().split(' ')
    cause, offstr, probAstr, probBstr = l.strip().split(' ')
    off = int(offstr)
    #pair = int(pairstr)
    probA = float(probAstr)
    probB = float(probBstr)
    #probs.update( {off: (cause, pair, probA, probB)} )
    probs.update( {off: (cause, probA, probB)} )


tsoutput = open(sys.argv[6], 'w')

class recog:
    def __init__(self, db, wins, svmpairs, svmpairsTam, probs):
        self.db = db
        self.wins = wins
        self.svmpairs = svmpairs
        self.svmpairsTam = svmpairsTam
        self.probs = probs

        self.direction = None

        self. off = None
        self.samples = None
        self.center = None
        #self.svmcause, self.svmpair, self.probA, self.probB = (None, None, None, None)
        self.svmcause, self.probA, self.probB = (None, None, None)
        self.pair = np.zeros(2, dtype=np.int64)

        self.templateA = None
        self.templateB = None
        self.lastCenterA = None
        self.lastCenterB = None

        self.lastTSA = None
        self.lastTSB = None
        self.lastIPIA = None
        self.lastIPIB = None

    def emitSingleA(self, sigs):
        self.templateA = sigs.copy() ###### Necessario? Nao irei alterar a variavel, apenas substitui-la
        self.templateAsize = self.samples
        self.lastCenterA = self.center
        recogdb.writeEntry(self.db, self.off, 1, 0, 0, 1<<30, 1<<30, 0, self.off+self.center, -1, self.svmcause, -1, self.probA, self.probB, list(sigs.values()))
        tsoutput.write('1 %d\n'%(self.off+self.center))

        if self.lastTSA is None:
            self.lastTSA = self.off+self.center
        else:
            self.lastIPIA = self.off+self.center - self.lastTSA
            self.lastTSA = self.off+self.center

    def emitSingleB(self,sigs):
        self.templateB = sigs.copy()
        self.templateBsize = self.samples
        self.lastCenterB = self.center
        recogdb.writeEntry(self.db, self.off, 2, 0, 1<<30, 0, 1<<30, 0, -1, self.off+self.center, self.svmcause, -1, self.probA, self.probB, list(sigs.values()))
        tsoutput.write('-1 %d\n'%(self.off+self.center))

        if self.lastTSB is None:
            self.lastTSB = self.off+self.center
        else:
            self.lastIPIB = self.off+self.center - self.lastTSB
            self.lastTSB = self.off+self.center

    def iterate(self, direction, cont=False):
        self.direction = direction
        if direction >= 0:
            winfunc = self.wins.nextWin
            singlefishIdx = 0
            adder = +1
        else:
            self.wins.end()
            winfunc = self.wins.prevWin
            singlefishIdx = svmpairsTam-1
            adder = -1 

        ret = not None
        while (ret is not None):
            tsoutput.flush()

            ret = winfunc()
            if ret is not None:
                lastLen, self.off, self.samples, channels, self.center, sigs = ret
                #self.svmcause, self.svmpair, self.probA, self.probB = self.probs[self.off]
                self.svmcause, self.probA, self.probB = self.probs[self.off]
            else:
                print('Spikes file ended')
                continue

            perc = 100.*self.off / (1.*self.svmpairs[-1,1])


            if singlefishIdx < svmpairsTam:
                self.pair[:] = svmpairs[singlefishIdx,:]

            if cont == True:
                if recogdb.verifyKey(self.db, self.off) is not None:
                    if self.off == self.pair[1]:
                        singlefishIdx += adder
                    print(self.off)
                    continue

            #print(self.off)

            if self.off == self.pair[1]:
                if self.pair[0] == 1:
                    if self.lastTSB is not None and self.lastIPIB is not None:
                        if (self.off+self.center > self.lastTSB + self.lastIPIB - overlapRange) and (self.off+self.center < self.lastTSB + self.lastIPIB + overlapRange):
                            sys.stdout.write('%d\t%.03f%%\tOverlap A predicted'%(self.off, perc))
                            sys.stdout.flush()
                            self.continuity(sigs)
                        else:

                            print('%d\t%.03f%%\tEmmiting single A\t%.02f%% A'%(self.off, perc, 100*self.probA))
                            self.emitSingleA(sigs)
                    else:

                        print('%d\t%.03f%%\tEmmiting single A\t%.02f%% A'%(self.off, perc, 100*self.probA))
                        self.emitSingleA(sigs)

                    singlefishIdx += adder
                else:
                    if self.lastTSA is not None and self.lastIPIA is not None:
                        if (self.off+self.center > self.lastTSA + self.lastIPIA - overlapRange) and (self.off+self.center < self.lastTSA + self.lastIPIA + overlapRange):
                            sys.stdout.write('%d\t%.03f%%\tOverlap B predicted'%(self.off, perc))
                            sys.stdout.flush()
                            self.continuity(sigs)
                        else:

                            print('%d\t%.03f%%\tEmmiting single B\t%.02f%% B'%(self.off, perc, 100*self.probB))
                            self.emitSingleB(sigs)
                    else:

                        print('%d\t%.03f%%\tEmmiting single B\t%.02f%% B'%(self.off, perc, 100*self.probB))
                        self.emitSingleB(sigs)
                    singlefishIdx += adder
            else:
                if (self.templateA is None) or (self.templateB is None):
                    print('%d\t%.03f%%\tLooking for first SVM'%(self.off, perc))
                    continue
                sys.stdout.write('%d\t%.03f%%\tCalling continuity'%(self.off, perc))
                sys.stdout.flush()
                self.continuity(sigs)

    def continuity(self, sigs):
        tamA = self.templateAsize
        tamB = self.templateBsize

        zfill = max(self.templateAsize, self.templateBsize) // 2
        data = np.array([])
        tempA = np.array([])
        tempB = np.array([])
        for ch, s in sigs.items():
            data = np.concatenate( (data, np.concatenate( (np.zeros(zfill), s, np.zeros(zfill)) )) )
            tempA = np.concatenate( (tempA, self.templateA[ch], np.zeros(2*zfill+s.size-tamA)) )
            tempB = np.concatenate( (tempB, self.templateB[ch], np.zeros(2*zfill+s.size-tamB)) )
        
        dif = np.zeros(data.size)

        tempsA = np.zeros((self.samples+2*zfill - tamA, tempA.size))
        for i in xrange(self.samples+2*zfill - tamA):
            tempsA[i,i:] = tempA[:tempA.size-i]
        tempsB = np.zeros((self.samples+2*zfill - tamB, tempB.size))
        for i in xrange(self.samples+2*zfill - tamB):
            tempsB[i,i:] = tempB[:tempB.size-i]

        # Minimize A
        sys.stdout.write('A ')
        sys.stdout.flush()
        distAm = np.array( [np.sum(np.absolute(data-tempsA[i,:])) for i in xrange(self.samples+2*zfill - tamA)] )
        posA = distAm.argmin()
        distA = distAm[posA]
        '''distA = np.inf
        for i in xrange(self.samples+2*zfill - tamA):
            distA_now = np.abs(data - tempsA[i,:]).sum()

            if distA_now < distA:
                distA = distA_now
                posA = i'''

        # Minimize B
        sys.stdout.write('B ')
        sys.stdout.flush()
        distBm = np.array( [np.sum(np.absolute(data-tempsB[i,:])) for i in xrange(self.samples+2*zfill - tamB)] )
        posB = distBm.argmin()
        distB = distBm[posB]
        '''distB = np.inf
        for i in xrange(self.samples+2*zfill - tamB):
            distB_now = np.abs(data - tempsB[i,:]).sum()

            if distB_now < distB:
                distB = distB_now
                posB = i'''

        import pymp
        distABm = pymp.shared.array( (self.samples+2*zfill - tamA, self.samples+2*zfill - tamB) ,dtype='float32')
        distABm.fill(np.inf)

        sys.stdout.write('AB ')
        sys.stdout.flush()
        with pymp.Parallel(4) as p:
            for i in xrange(self.samples+2*zfill - tamA):
                tA = tempsA[i,:]
                for j in p.range(self.samples+2*zfill - tamB):
                    distABm[i,j] = np.sum(np.absolute(data - tA - tempsB[j,:]))
                
        posA_AB, posB_AB = np.unravel_index(distABm.argmin(), distABm.shape)
        distAB = distABm[posA_AB, posB_AB]

        sys.stdout.write('distsOk ')
        sys.stdout.flush()
        if False:
            import matplotlib.pyplot as plt

            plt.figure(1, figsize=(22,16))

            ax1 = plt.subplot2grid((3,4), (0,0),colspan=3)
            if distA < distB and distA < distAB:
                plt.title('A')
            elif distB < distA and distB < distAB:
                plt.title('B')
            elif distAB <= distA and distAB <= distB:
                plt.title('AB')

            plt.plot(data, 'k-', alpha=1.0)
            plt.plot(np.arange(posA, tempA.size-1), tempA[:-posA-1], 'b-', alpha=0.5)
            for i in xrange(11):
                posinicial = i*(self.samples+2*zfill)
                plt.plot([posinicial+posA+self.lastCenterA, posinicial+posA+self.lastCenterA], [-10,10], 'b-', alpha=0.3)

            ax2 = plt.subplot2grid((3,4), (1,0), sharex=ax1, sharey=ax1, colspan=3)
            plt.plot(data, 'k-', alpha=1.0)
            plt.plot(np.arange(posB, tempB.size-1), tempB[:-posB-1], 'r-', alpha=0.5)
            for i in xrange(11):
                posinicial = i*(self.samples+2*zfill)
                plt.plot([posinicial+posB+self.lastCenterB, posinicial+posB+self.lastCenterB], [-10,10], 'r-', alpha=0.3)

            ax3 = plt.subplot2grid((3,4), (2,0), sharex=ax1, sharey=ax1,colspan=3)
            plt.plot(data, 'k-', alpha=1.0)
            plt.plot(np.arange(posA_AB, tempA.size-1), tempA[:-posA_AB-1], 'b-', alpha=0.5)
            plt.plot(np.arange(posB_AB, tempB.size-1), tempB[:-posB_AB-1], 'r-', alpha=0.5)
            for i in xrange(11):
                posinicial = i*(self.samples+2*zfill)
                plt.plot([posinicial+posA_AB+self.lastCenterA, posinicial+posA_AB+self.lastCenterA], [-10,10], 'b-', alpha=0.3)
                plt.plot([posinicial+posB_AB+self.lastCenterB, posinicial+posB_AB+self.lastCenterB], [-10,10], 'r-', alpha=0.3)

            ax4 = plt.subplot2grid((3,4), (0,3))
            plt.plot(distAm)

            ax5 = plt.subplot2grid((3,4), (1,3))
            plt.plot(distBm)

            ax6 = plt.subplot2grid((3,4), (2,3))
            plt.pcolormesh(distABm)
            plt.axis('tight')
            plt.colorbar()

            plt.show()

        ###########################################
        ############### Verificar se existe no db #
        ###########################################
        tup = recogdb.readHeaderEntry(self.db,self.off)
        if tup is not None:
            off, data, spkwin = tup

            mindist = min(distA, distB, distAB)
            dbdistA = data[ recogdb.dicFields['distA'] ]
            dbdistB = data[ recogdb.dicFields['distB'] ]
            dbdistAB = data[ recogdb.dicFields['distAB'] ]
            mindistDB = min(dbdistA, dbdistB, dbdistAB)
            if mindistDB < mindist:
                print('Leaving DB as is')
                return None

        if distA < distB and distA < distAB:
            recogdb.writeEntry(self.db, self.off, 1, self.direction, distA, distB, distAB, 0, self.off+posA, -1, self.svmcause, -1, self.probA, self.probB, list(sigs.values()))
            tsoutput.write('1 %d\n'%(self.off+posA))
            sys.stdout.write('\tsingle A')
            sys.stdout.flush()

            # Replace template
            self.templateA = sigs.copy()
            self.templateAsize = self.samples
            self.lastCenterA = posA

            if self.lastTSA is None:
                self.lastTSA = self.off+posA
            else:
                self.lastIPIA = self.off+posA - self.lastTSA
                self.lastTSA = self.off+posA

        elif distB < distA and distB < distAB:
            recogdb.writeEntry(self.db, self.off, 2, self.direction, distA, distB, distAB, 0, -1, self.off+posB, self.svmcause, -1, self.probA, self.probB, list(sigs.values()))
            tsoutput.write('-1 %d\n'%(self.off+posB))
            sys.stdout.write('\tsingle B')
            sys.stdout.flush()

            # Replace template
            self.templateB = sigs.copy()
            self.templateBsize = self.samples
            self.lastCenterB = posB

            if self.lastTSB is None:
                self.lastTSB = self.off+posB
            else:
                self.lastIPIB = self.off+posB - self.lastTSB
                self.lastTSB = self.off+posB

        elif distAB <= distA and distAB <= distB:
            recogdb.writeEntry(self.db, self.off, 3, self.direction, distA, distB, distAB, 0, self.off+posA_AB, self.off+posB_AB, self.svmcause, -1, self.probA, self.probB, list(sigs.values()))
            if posA < posB:
                tsoutput.write('1 %d\n'%(self.off+posA_AB))
                tsoutput.write('-1 %d\n'%(self.off+posB_AB))
                sys.stdout.write('\toverlap AB')
                sys.stdout.flush()
            else:
                tsoutput.write('-1 %d\n'%(self.off+posB_AB))
                tsoutput.write('1 %d\n'%(self.off+posA_AB))
                sys.stdout.write('\toverlap BA')
                sys.stdout.flush()

            if self.lastTSA is None:
                self.lastTSA = self.off+posA_AB
            else:
                self.lastIPIA = self.off+posA_AB - self.lastTSA
                self.lastTSA = self.off+posA_AB

            if self.lastTSB is None:
                self.lastTSB = self.off+posB_AB
            else:
                self.lastIPIB = self.off+posB_AB - self.lastTSB
                self.lastTSB = self.off+posB_AB

        sys.stdout.write('\n')
        sys.stdout.flush()

    def export(self):
        print('exporting data to' + tsoutput.name)
        for rec in self.db.iteritems():
            key, bindata = rec
            off, = struct.unpack('q', key)
            sys.stdout.write('\r%d'%off)
            sys.stdout.flush()
            presentFish, direction, distA, distB, distAB, flags, correctedPosA, correctedPosB, svm, pairsvm, probA, probB, spkdata = recogdb.parseDBHeader(bindata)
            if presentFish == 1:
                tsoutput.write('1 %d\n'%correctedPosA)
            elif presentFish == 2:
                tsoutput.write('-1 %d\n'%correctedPosB)
            elif presentFish == 3:
                if correctedPosA < correctedPosB:
                    tsoutput.write('1 %d\n'%correctedPosA)
                    tsoutput.write('-1 %d\n'%correctedPosB)
                else:
                    tsoutput.write('-1 %d\n'%correctedPosB)
                    tsoutput.write('1 %d\n'%correctedPosA)
            else:
                print('error on presentFish DB field')
            tsoutput.flush()


if __name__ == '__main__':
    r = recog(db, wins, svmpairs, svmpairsTam, probs)
    if sys.argv[1] == 'iterate':
        r.iterate(direction)

    elif sys.argv[1] == 'continue':
        r.iterate(direction, cont=True)

    elif sys.argv[1] == 'export':
        r.export()
















    # Backwards
    '''wins.end()
    i=0
    while True:
        i += 1
        ret = wins.prevWin()
        if ret is not None:
            lastLen, off, samples, channels, center, sigs = ret
        else:
            break
        print('\nstep: %d'%i)
        for c, s in sigs:
            plt.plot(s)
        plt.show()'''


    # Foreward
    '''i=0
    while True:
        i += 1
        print('\nstep: %d'%i)
        ret = wins.nextWin()
        if ret is not None:
            lastLen, off, samples, channels, sigs, center = ret
        else:
            break
        for c, s in sigs:
            plt.plot(s)

        plt.show()'''
