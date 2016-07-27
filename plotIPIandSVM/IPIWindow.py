from PyQt4 import QtCore, QtGui
from IPIClick_interface import *
from single2overlap import single2overlap

import random

import numpy as np

import sys, os
if sys.version_info.major == 3:
    xrange = range

if os.getcwd().split('/')[-1] == 'gui':
    sys.path.append( os.path.realpath('../python') )
elif os.getcwd().split('/')[-1] == 'plotIPIandSVM':
    sys.path.append( os.path.realpath('../') )
import recogdb

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

NChan = 11

INVERTION = 0
SINGLE2OVERLAP = 1
CREATESVM = 2
CONVERT2SINGLEA = 3
CONVERT2SINGLEB = 4
CHANGEOVERLAPPOSITION = 5
SVMINVERTION = 6
SVMREMOVE = 7
RECOGFUTURE = 8
RECOGPAST = 9

dicUndo = {INVERTION: 'Continuity invertion',
           SINGLE2OVERLAP: 'Single spike converted to overlap',
           CREATESVM: 'SVM pair created',
           CONVERT2SINGLEA: 'Convert overlap to single A fish',
           CONVERT2SINGLEB: 'Convert overlap to single B fish',
           CHANGEOVERLAPPOSITION: 'Changes spikes positioning',
           SVMINVERTION: 'SVM inverted',
           SVMREMOVE: 'SVM removed', 
           RECOGFUTURE: 'Continuity enforced from this SVM to the future', 
           RECOGPAST: 'Continuity enforced from this SVM to the past', 
}

dicFields = {'presentFish': 'int',
        'direction': 'int',
        'distA': 'float',
        'distB': 'float',
        'distAB': 'float',
        'flags': 'int',
        'correctedPosA': 'int',
        'correctedPosB': 'int',
        'svm': 'char',
        'pairsvm': 'int',
        'probA': 'float',
        'probB': 'float',
}

class ModifySelector:
    def __init__(self, db, undoFilename, folder, datafile):
        self.db = db
        self.undoFilename = undoFilename
        self.folder = folder
        
        self.single2overlapWindow = single2overlap(db, NChan, datafile)
        
        # if to avoid warning of loadtxt from empty file
        if os.stat(undoFilename).st_size != 0:
            self.undoKeys = set(np.loadtxt(undoFilename, unpack=True, ndmin=1))
        else:
            self.undoKeys = set()
        
        self.undoSVM = False
        self.replot = False

    # undoList = [ ( Action, {Fields: (Old, New)}, hashUndo ), ( Action, {Fields: (Old, New)}, hashUndo ), ... ]
    def parseModifications(self, key):
        modFilename = self.folder + '/' + str(key) + '.undo'
        if not os.path.isfile(modFilename):
            return None
        modFile = open(modFilename, 'r')
        
        undoList = []
        ActionNow = ''
        dicActions = {}
        hashUndo = 0
        for l in modFile.xreadlines():
            Columns = l.split('\t')
            
            # Action identifier
            if Columns[0] != '':
                if (len(dicActions.keys()) != 0) or (ActionNow in [ dicUndo[RECOGFUTURE], dicUndo[RECOGPAST] ]):
                    undoList.append( (ActionNow, dicActions, hashUndo) ) 
                    
                ActionNow = Columns[0].strip() # remove last '\n'
                hashUndo = int(Columns[1].strip())
                assert ( ActionNow in dicUndo.values() )
                dicActions = {}
                continue
            
            # Field identifier
            Field = Columns[1].strip()
            OldValue = Columns[2].strip()
            NewValue = Columns[3].strip()
            
            assert ( Field in recogdb.dicFields.keys() )
            
            dicActions[Field] = (OldValue, NewValue)
           
        # Append last action 
        undoList.append( (ActionNow, dicActions, hashUndo) ) 
        # List is from the newest to the oldest modification
        return undoList[::-1]
    
    def regenUndoFile(self, key, modListInv):
        # File is generated on chronological order
        modList = modListInv[::-1]
        
        # Remove from undokeys list if is the oldest alteration
        if len(modList) == 0:
            undoFile = open(self.undoFilename, 'r')
            lines = undoFile.readlines()
            undoFile.close()
            
            undoFile = open(self.undoFilename, 'w')
            for l in lines:
                if l != str(key)+'\n':
                    undoFile.write(l)
            undoFile.close()
        
        keyundofile = open(self.folder + '/' + str(key) + '.undo', 'w')
        for action, dicAction, hashUndo in modList:
            keyundofile.write( "%s\t%d\n"%(action,hashUndo) )
            for field in dicAction.keys():
                assert dicFields[field] in ('int', 'float', 'char')
                dataold, datanew = dicAction[field]
                if dicFields[field] == 'float':
                    keyundofile.write("\t%s\t%f\t%f\n"%(field, float(dataold), float(datanew)))
                elif dicFields[field] == 'int':
                    keyundofile.write("\t%s\t%d\t%d\n"%(field, int(dataold), int(datanew)))
                elif dicFields[field] == 'char':
                    keyundofile.write("\t%s\t%c\t%c\n"%(field, dataold, datanew))
        keyundofile.close()
        
        if os.stat(keyundofile.name).st_size == 0:
            os.remove(keyundofile.name)

    def invertIPI(self, key):
        if key not in self.undoKeys:
            undoFile = open(self.undoFilename, 'a')
            undoFile.write('%d\n'%key)
            undoFile.flush()
            undoFile.close()
        
        keyundofile = open(self.folder + '/' + str(key) + '.undo', 'a')
        
        off, read_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        
        # Store old SVM data on DB (it will change to 'm' - Manually)
        oldSVM = read_data[ recogdb.dicFields['svm'] ]
        
        # Store old 'presentFish' data
        oldFish = read_data[ recogdb.dicFields['presentFish'] ]
        if oldFish not in (1,2):
            sys.stdout.write('only single spikes can be inverted')
            sys.stdout.flush()
            assert False
        newFish = 2 if oldFish == 1 else 1
        
        # Store old correctedPos data - The fields must be inverted
        oldCorrectedPosA = read_data[ recogdb.dicFields['correctedPosA'] ]
        oldCorrectedPosB = read_data[ recogdb.dicFields['correctedPosB'] ]
        if newFish == 1:
            newCorrectedPosA = oldCorrectedPosB
            newCorrectedPosB = -1
        else:
            newCorrectedPosA = -1
            newCorrectedPosB = oldCorrectedPosA
        
        # Store the old dists fields - They are put to a minimum acording the the fish
        # So the continuity will no overwrite them
        oldDistA = read_data[ recogdb.dicFields['distA'] ]
        oldDistB = read_data[ recogdb.dicFields['distB'] ]
        oldDistAB = read_data[ recogdb.dicFields['distAB'] ]
        if newFish == 1:
            newDistA = 0.
            newDistB = float('Inf')
            newDistAB = float('Inf')
        else:
            newDistA = float('Inf')
            newDistB = 0.
            newDistAB = float('Inf')
        
        
        # Update DB
        recogdb.updateHeaderEntry(self.db, key, 'presentFish', newFish, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'correctedPosA', newCorrectedPosA, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'correctedPosB', newCorrectedPosB, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distA', newDistA, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distB', newDistB, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distAB', newDistAB, sync=True)
        
        off, new_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        
        newSVM = new_data[ recogdb.dicFields['svm'] ]
        newFish = new_data[ recogdb.dicFields['presentFish'] ]
        newCorrectedPosA = new_data[ recogdb.dicFields['correctedPosA'] ]
        newCorrectedPosB = new_data[ recogdb.dicFields['correctedPosB'] ]
        newDistA = new_data[ recogdb.dicFields['distA'] ]
        newDistB = new_data[ recogdb.dicFields['distB'] ]
        newDistAB = new_data[ recogdb.dicFields['distAB'] ]
        
        # Action identifier
        hashUndo = random.randint(0, 2**64-1)
        keyundofile.write( '%s\t%d\n'%(dicUndo[INVERTION], hashUndo) )
        
        # Modified fields
        keyundofile.write( '\t%s\t%c\t%c\n'%('svm', oldSVM, newSVM) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('presentFish', oldFish, newFish) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('correctedPosA', oldCorrectedPosA, newCorrectedPosA) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('correctedPosB', oldCorrectedPosB, newCorrectedPosB) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distA', oldDistA, newDistA) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distB', oldDistB, newDistB) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB, newDistAB) )
        
        keyundofile.close()
    
    def convert2overlap(self,key):
        prevB, data_pB = recogdb.getNearest(self.db, -1, key, 1, overlap=True)
        prevR, data_pR = recogdb.getNearest(self.db, -1, key, 2, overlap=True)

        off_now, data_now = recogdb.get_location(self.db, key)
        
        nextB, data_nB = recogdb.getNearest(self.db,  1, key, 1, overlap=True)
        nextR, data_nR = recogdb.getNearest(self.db,  1, key, 2, overlap=True)
        
        data = ((prevB, data_pB), \
                (prevR, data_pR), \
                (off_now, data_now), \
                (nextB, data_nB), \
                (nextR, data_nR))
        
        self.single2overlapWindow.plotSignals(data, channel=0)
        self.single2overlapWindow.exec_()
        if (self.single2overlapWindow.posA != None) and \
           (self.single2overlapWindow.posB != None):
            self.convert2overlapOnDB(key, \
                                     self.single2overlapWindow.posA, \
                                     self.single2overlapWindow.posB)
    
    def convert2overlapOnDB(self, key, posA, posB):
        # Used to change spike positioning too
        if key not in self.undoKeys:
            undoFile = open(self.undoFilename, 'a')
            undoFile.write('%d\n'%key)
            undoFile.flush()
            undoFile.close()
        
        keyundofile = open(self.folder + '/' + str(key) + '.undo', 'a')
        
        off, read_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        
        # Store old SVM data on DB (it will change to 'm' - Manually)
        oldSVM = read_data[ recogdb.dicFields['svm'] ]
        
        # Store old 'presentFish' data
        oldFish = read_data[ recogdb.dicFields['presentFish'] ]
        newFish = 3
        
        # Store old correctedPos data
        oldCorrectedPosA = read_data[ recogdb.dicFields['correctedPosA'] ]
        oldCorrectedPosB = read_data[ recogdb.dicFields['correctedPosB'] ]
        
        newCorrectedPosA = posA
        newCorrectedPosB = posB
        
        # Store the old dists fields - They are put to a minimum acording the the fish
        # So the continuity will no overwrite them
        oldDistA = read_data[ recogdb.dicFields['distA'] ]
        oldDistB = read_data[ recogdb.dicFields['distB'] ]
        oldDistAB = read_data[ recogdb.dicFields['distAB'] ]
        
        newDistA = float('Inf')
        newDistB = float('Inf')
        newDistAB = 0.
        
        # Update DB
        recogdb.updateHeaderEntry(self.db, key, 'presentFish', newFish, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'correctedPosA', newCorrectedPosA, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'correctedPosB', newCorrectedPosB, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distA', newDistA, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distB', newDistB, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distAB', newDistAB, sync=True)
        
        off, new_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        
        newSVM = new_data[ recogdb.dicFields['svm'] ]
        newFish = new_data[ recogdb.dicFields['presentFish'] ]
        newCorrectedPosA = new_data[ recogdb.dicFields['correctedPosA'] ]
        newCorrectedPosB = new_data[ recogdb.dicFields['correctedPosB'] ]
        newDistA = new_data[ recogdb.dicFields['distA'] ]
        newDistB = new_data[ recogdb.dicFields['distB'] ]
        newDistAB = new_data[ recogdb.dicFields['distAB'] ]
        
        # Action identifier
        hashUndo = random.randint(0, 2**64-1)
        if oldFish in [1, 2]:
            keyundofile.write( '%s\t%d\n'%(dicUndo[SINGLE2OVERLAP], hashUndo) )
        else:
            keyundofile.write( '%s\t%d\n'%(dicUndo[CHANGEOVERLAPPOSITION], hashUndo) )
        
        # Modified fields
        keyundofile.write( '\t%s\t%c\t%c\n'%('svm', oldSVM, newSVM) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('presentFish', oldFish, newFish) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('correctedPosA', oldCorrectedPosA, newCorrectedPosA) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('correctedPosB', oldCorrectedPosB, newCorrectedPosB) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distA', oldDistA, newDistA) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distB', oldDistB, newDistB) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB, newDistAB) )
        
        keyundofile.close()
    
    def createSVMPair(self, key):
        off, read_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        fish = read_data[ recogdb.dicFields['presentFish'] ]
        assert fish in [1,2]
        other_fish = ( set([1,2]) - set([fish]) ).pop()
        
        offN, dataN = recogdb.getNearest(self.db, 1, key, other_fish, overlap=True)
        fishN = dataN[ recogdb.dicFields['presentFish'] ]
        svmN = dataN[ recogdb.dicFields['svm'] ]
        Next = (fishN != 3) and (svmN != 's') # False if overlap or svm
    
        offP, dataP = recogdb.getNearest(self.db, -1, key, other_fish, overlap=True)
        fishP = dataP[ recogdb.dicFields['presentFish'] ]
        svmP = dataP[ recogdb.dicFields['svm'] ]
        Prev = (fishP != 3) and (svmP != 's') # False if overlap or svm
        
        msgbox = QtGui.QMessageBox()
        msgbox.setText('Create SVM with the next or with the previous? (Only non-SVM single spikes can be used)')

        returnValues = []
        
        if Prev == True:
            msgbox.addButton(QtGui.QPushButton('Previous'), QtGui.QMessageBox.NoRole)
            returnValues.append(offP)
        else:
            msgbox.addButton(QtGui.QMessageBox.NoButton)
            
        msgbox.addButton(QtGui.QMessageBox.Cancel)
        
        if Next == True:
            msgbox.addButton(QtGui.QPushButton('Next'), QtGui.QMessageBox.YesRole)
            returnValues.append(offN)
        else:
            msgbox.addButton(QtGui.QMessageBox.NoButton)
            
        ret = msgbox.exec_()
        
        if ret == QtGui.QMessageBox.Cancel:
            self.replot = False
            return None
        
        self.createSVMPairOnDB(off, returnValues[ret])
        self.replot = True
        
    def createSVMPairOnDB(self, key1, key2):
        if key1 not in self.undoKeys:
            undoFile = open(self.undoFilename, 'a')
            undoFile.write('%d\n'%key1)
            undoFile.flush()
            undoFile.close()
        if key2 not in self.undoKeys:
            undoFile = open(self.undoFilename, 'a')
            undoFile.write('%d\n'%key2)
            undoFile.flush()
            undoFile.close()
        
        keyundofile1 = open(self.folder + '/' + str(key1) + '.undo', 'a')
        keyundofile2 = open(self.folder + '/' + str(key2) + '.undo', 'a')
        
        # Read old data
        off1, read_data1, spkdata1 = recogdb.readHeaderEntry(self.db, key1)
        off2, read_data2, spkdata2 = recogdb.readHeaderEntry(self.db, key2)
        
        oldSVM1 = read_data1[ recogdb.dicFields['svm'] ]
        oldSVM2 = read_data2[ recogdb.dicFields['svm'] ]
        
        oldPair1 = read_data1[ recogdb.dicFields['pairsvm'] ]
        oldPair2 = read_data2[ recogdb.dicFields['pairsvm'] ]
        
        presentFish1 = read_data1[ recogdb.dicFields['presentFish'] ]
        presentFish2 = read_data2[ recogdb.dicFields['presentFish'] ]
        
        oldDistA1 = read_data1[ recogdb.dicFields['distA'] ]
        oldDistB1 = read_data1[ recogdb.dicFields['distB'] ]
        oldDistAB1 = read_data1[ recogdb.dicFields['distAB'] ]
        
        oldDistA2 = read_data2[ recogdb.dicFields['distA'] ]
        oldDistB2 = read_data2[ recogdb.dicFields['distB'] ]
        oldDistAB2 = read_data2[ recogdb.dicFields['distAB'] ]
        
        # Manually modified SVM
        newSVM1 = 'v'
        newSVM2 = 'v'
        
        newPair1 = off2
        newPair2 = off1
        
        assert (presentFish1 in [1,2])
        if presentFish1 == 1:
            newDistA1 = 0.
            newDistB1 = float('Inf')
        else:
            newDistA1 = float('Inf')
            newDistB1 = 0.
        newDistAB1 = float('Inf')
        
        assert (presentFish2 in [1,2])
        if presentFish2 == 1:
            newDistA2 = 0.
            newDistB2 = float('Inf')
        else:
            newDistA2 = float('Inf')
            newDistB2 = 0.
        newDistAB2 = float('Inf')
        
        # Update DB
        recogdb.updateHeaderEntry(self.db, key1, 'svm', newSVM1, sync=False)
        recogdb.updateHeaderEntry(self.db, key2, 'svm', newSVM2, sync=False)
        
        recogdb.updateHeaderEntry(self.db, key1, 'pairsvm', newPair1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'pairsvm', newPair2, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key1, 'distA', newDistA1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key1, 'distB', newDistB1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key1, 'distAB', newDistAB1, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key2, 'distA', newDistA2, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'distB', newDistB2, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'distAB', newDistAB2, sync=True, change_svm=False)
        
        # Read new data
        off1, new_data1, spkdata1 = recogdb.readHeaderEntry(self.db, key1)
        off2, new_data2, spkdata2 = recogdb.readHeaderEntry(self.db, key2)
        
        newSVM1 = new_data1[ recogdb.dicFields['svm'] ]
        newSVM2 = new_data2[ recogdb.dicFields['svm'] ]
        
        newPair1 = new_data1[ recogdb.dicFields['pairsvm'] ]
        newPair2 = new_data2[ recogdb.dicFields['pairsvm'] ]
        
        newDistA1 = new_data1[ recogdb.dicFields['distA'] ]
        newDistB1 = new_data1[ recogdb.dicFields['distB'] ]
        newDistAB1 = new_data1[ recogdb.dicFields['distAB'] ]
        
        newDistA2 = new_data2[ recogdb.dicFields['distA'] ]
        newDistB2 = new_data2[ recogdb.dicFields['distB'] ]
        newDistAB2 = new_data2[ recogdb.dicFields['distAB'] ]
        
        # Action identifier
        hashUndo = random.randint(0, 2**64-1)
        keyundofile1.write( '%s\t%d\n'%(dicUndo[CREATESVM], hashUndo) )
        keyundofile2.write( '%s\t%d\n'%(dicUndo[CREATESVM], hashUndo) )
        
        # Modified Fields
        keyundofile1.write( '\t%s\t%c\t%c\n'%('svm', oldSVM1, newSVM1) )
        keyundofile2.write( '\t%s\t%c\t%c\n'%('svm', oldSVM2, newSVM2) )
        
        keyundofile1.write( '\t%s\t%d\t%d\n'%('pairsvm', oldPair1, newPair1) )
        keyundofile2.write( '\t%s\t%d\t%d\n'%('pairsvm', oldPair2, newPair2) )
        
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distA', oldDistA1, newDistA1) )
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distB', oldDistB1, newDistB1) )
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB1, newDistAB1) )
        
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distA', oldDistA2, newDistA2) )
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distB', oldDistB2, newDistB2) )
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB2, newDistAB2) )
        
        keyundofile1.close()
        keyundofile2.close()
    
    def overlap2single(self, key, fish):
        if key not in self.undoKeys:
            undoFile = open(self.undoFilename, 'a')
            undoFile.write('%s\n'%key)
            undoFile.flush()
            undoFile.close()
        
        assert fish in ['A', 'B']
        
        keyundofile = open(self.folder + '/' + str(key) + '.undo', 'a')
        
        # Read old data
        off, read_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        
        oldPresentFish = read_data[ recogdb.dicFields['presentFish'] ]
        
        oldDistA = read_data[ recogdb.dicFields['distA'] ]
        oldDistB = read_data[ recogdb.dicFields['distB'] ]
        oldDistAB = read_data[ recogdb.dicFields['distAB'] ]
        
        oldCorrectedPosA = read_data[ recogdb.dicFields['correctedPosA'] ]
        oldCorrectedPosB = read_data[ recogdb.dicFields['correctedPosB'] ]
        
        assert oldPresentFish == 3
        
        if fish == 'A':
            newPresentFish = 1
            
            newDistA = 0.
            newDistB = float('Inf')
            newDistAB = float('Inf')
        elif fish == 'B':
            newPresentFish = 2
            
            newDistA = float('Inf')
            newDistB = 0.
            newDistAB = float('Inf')
       
        # Will pass dectectIPI again to select the better position
        newCorrectedPosA = -1
        newCorrectedPosB = -1
        
        # UpdateDB
        recogdb.updateHeaderEntry(self.db, key, 'presentFish', newPresentFish, sync=False)
        
        recogdb.updateHeaderEntry(self.db, key, 'distA', newDistA, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distB', newDistB, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'distAB', newDistAB, sync=False)
        
        recogdb.updateHeaderEntry(self.db, key, 'correctedPosA', newCorrectedPosA, sync=False)
        recogdb.updateHeaderEntry(self.db, key, 'correctedPosB', newCorrectedPosB, sync=True)
        
        # Read new Data
        off, new_data, spkdata = recogdb.readHeaderEntry(self.db, key)
        
        newPresentFish = new_data[ recogdb.dicFields['presentFish'] ]
        
        newDistA = new_data[ recogdb.dicFields['distA'] ]
        newDistB = new_data[ recogdb.dicFields['distB'] ]
        newDistAB = new_data[ recogdb.dicFields['distAB'] ]
        
        newCorrectedPosA = new_data[ recogdb.dicFields['correctedPosA'] ]
        newCorrectedPosB = new_data[ recogdb.dicFields['correctedPosB'] ]
        
        # Action identifier
        hashUndo = random.randint(0, 2**64-1)
        if fish == 'A':
            keyundofile.write( '%s\t%d\n'%(dicUndo[CONVERT2SINGLEA], hashUndo) )
        elif fish == 'B':
            keyundofile.write( '%s\t%d\n'%(dicUndo[CONVERT2SINGLEB], hashUndo) )
        
        # Modified Fields
        keyundofile.write( '\t%s\t%d\t%d\n'%('presentFish', oldPresentFish, newPresentFish) )
    
        keyundofile.write( '\t%s\t%f\t%f\n'%('distA', oldDistA, newDistA) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distB', oldDistB, newDistB) )
        keyundofile.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB, newDistAB) )
        
        keyundofile.write( '\t%s\t%d\t%d\n'%('correctedPosA', oldCorrectedPosA, newCorrectedPosA) )
        keyundofile.write( '\t%s\t%d\t%d\n'%('correctedPosB', oldCorrectedPosB, newCorrectedPosB) )
        
        keyundofile.close()
    
    def invertSVM(self, key):
        
        # Read pair keys
        off1, read_data1, spk_data1 = recogdb.readHeaderEntry(self.db, key)
        
        key1 = off1
        key2 = read_data1[ recogdb.dicFields['pairsvm'] ]
        
        off2, read_data2, spk_data2 = recogdb.readHeaderEntry(self.db, key2)
        
        # Open undo files
        if key1 not in self.undoKeys:
            undoFile1 = open(self.undoFilename, 'a')
            undoFile1.write('%s\n'%key1)
            undoFile1.flush()
            undoFile1.close()
        keyundofile1 = open(self.folder + '/' + str(key1) + '.undo', 'a')
        
        if key2 not in self.undoKeys:
            undoFile2 = open(self.undoFilename, 'a')
            undoFile2.write('%s\n'%key2)
            undoFile2.flush()
            undoFile2.close()
        keyundofile2 = open(self.folder + '/' + str(key2) + '.undo', 'a')
        
        # Read old data
        oldFish1 = read_data1[ recogdb.dicFields['presentFish'] ]
        if oldFish1 not in (1,2):
            sys.stdout.write('only single spikes can be inverted')
            sys.stdout.flush()
            assert False
        newFish1 = 2 if oldFish1 == 1 else 1
        
        oldFish2 = read_data2[ recogdb.dicFields['presentFish'] ]
        if oldFish2 not in (1,2):
            sys.stdout.write('only single spikes can be inverted')
            sys.stdout.flush()
            assert False
        newFish2 = 2 if oldFish2 == 1 else 1
        
        oldProbA1 = read_data1[ recogdb.dicFields['probA'] ]
        oldProbB1 = read_data1[ recogdb.dicFields['probB'] ]
        
        oldProbA2 = read_data2[ recogdb.dicFields['probA'] ]
        oldProbB2 = read_data2[ recogdb.dicFields['probB'] ]
        
        oldDistA1 = read_data1[ recogdb.dicFields['distA'] ]
        oldDistB1 = read_data1[ recogdb.dicFields['distB'] ]
        oldDistAB1 = read_data1[ recogdb.dicFields['distAB'] ]
        
        oldDistA2 = read_data2[ recogdb.dicFields['distA'] ]
        oldDistB2 = read_data2[ recogdb.dicFields['distB'] ]
        oldDistAB2 = read_data2[ recogdb.dicFields['distAB'] ]
        
        oldCorrectedPosA1 = read_data1[ recogdb.dicFields['correctedPosA'] ]
        oldCorrectedPosB1 = read_data1[ recogdb.dicFields['correctedPosB'] ]
        
        oldCorrectedPosA2 = read_data2[ recogdb.dicFields['correctedPosA'] ]
        oldCorrectedPosB2 = read_data2[ recogdb.dicFields['correctedPosB'] ]
        
        oldSVM1 = read_data1[ recogdb.dicFields['svm'] ]
        oldSVM2 = read_data2[ recogdb.dicFields['svm'] ]
        
        if newFish1 == 1:
            newProbA1 = 1.
            newProbB1 = 0.
            
            newDistA1 = 0.
            newDistB1 = float('Inf')
        else:
            newProbA1 = 0.
            newProbB1 = 1.
            
            newDistA1 = float('Inf')
            newDistB1 = 0.
        
        newDistAB1 = float('Inf')
        
        if newFish2 == 1:
            newProbA2 = 1.
            newProbB2 = 0.
            
            newDistA2 = 0.
            newDistB2 = float('Inf')
        else:
            newProbA2 = 0.
            newProbB2 = 1.
            
            newDistA2 = float('Inf')
            newDistB2 = 0.
        
        newDistAB2 = float('Inf')
        
        newCorrectedPosA1 = oldCorrectedPosB1
        newCorrectedPosB1 = oldCorrectedPosA1
        
        newCorrectedPosA2 = oldCorrectedPosB2
        newCorrectedPosB2 = oldCorrectedPosA2
        
        newSVM1 = 'v'
        newSVM2 = 'v'
        
        # Update DB
        recogdb.updateHeaderEntry(self.db, key1, 'svm', newSVM1, sync=False)
        recogdb.updateHeaderEntry(self.db, key2, 'svm', newSVM2, sync=False)
        
        recogdb.updateHeaderEntry(self.db, key1, 'presentFish', newFish1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'presentFish', newFish2, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key1, 'correctedPosA', newCorrectedPosA1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key1, 'correctedPosB', newCorrectedPosB1, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key2, 'correctedPosA', newCorrectedPosA2, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'correctedPosB', newCorrectedPosB2, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key1, 'probA', newProbA1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key1, 'probB', newProbB1, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key2, 'probA', newProbA2, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'probB', newProbB2, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key1, 'distA', newDistA1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key1, 'distB', newDistB1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key1, 'distAB', newDistAB1, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key2, 'distA', newDistA2, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'distB', newDistB2, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'distAB', newDistAB2, sync=True, change_svm=False)
        
        # Read new data
        off1, new_data1, spk_data1 = recogdb.readHeaderEntry(self.db, key1)
        off2, new_data2, spk_data2 = recogdb.readHeaderEntry(self.db, key2)
        
        newFish1 = new_data1[ recogdb.dicFields['presentFish'] ]
        newFish2 = new_data2[ recogdb.dicFields['presentFish'] ]
        
        newProbA1 = new_data1[ recogdb.dicFields['probA'] ]
        newProbB1 = new_data1[ recogdb.dicFields['probB'] ]
        
        newProbA2 = new_data2[ recogdb.dicFields['probA'] ]
        newProbB2 = new_data2[ recogdb.dicFields['probB'] ]
        
        newDistA1 = new_data1[ recogdb.dicFields['distA'] ]
        newDistB1 = new_data1[ recogdb.dicFields['distB'] ]
        newDistAB1 = new_data1[ recogdb.dicFields['distAB'] ]
        
        newDistA2 = new_data2[ recogdb.dicFields['distA'] ]
        newDistB2 = new_data2[ recogdb.dicFields['distB'] ]
        newDistAB2 = new_data2[ recogdb.dicFields['distAB'] ]
        
        newCorrectedPosA1 = new_data1[ recogdb.dicFields['correctedPosA'] ]
        newCorrectedPosB1 = new_data1[ recogdb.dicFields['correctedPosB'] ]
        
        newCorrectedPosA2 = new_data2[ recogdb.dicFields['correctedPosA'] ]
        newCorrectedPosB2 = new_data2[ recogdb.dicFields['correctedPosB'] ]
        
        newSVM1 = new_data1[ recogdb.dicFields['svm'] ]
        newSVM2 = new_data2[ recogdb.dicFields['svm'] ]
        
        # Action identifier
        hashUndo = random.randint(0, 2**64-1)
        keyundofile1.write( '%s\t%d\n'%(dicUndo[SVMINVERTION], hashUndo) )
        keyundofile2.write( '%s\t%d\n'%(dicUndo[SVMINVERTION], hashUndo) )
        
        # Modified Fields
        keyundofile1.write( '\t%s\t%c\t%c\n'%('svm', oldSVM1, newSVM1) )
        keyundofile2.write( '\t%s\t%c\t%c\n'%('svm', oldSVM2, newSVM2) )
        
        keyundofile1.write( '\t%s\t%d\t%d\n'%('presentFish', oldFish1, newFish1) )
        keyundofile2.write( '\t%s\t%d\t%d\n'%('presentFish', oldFish2, newFish2) )
    
        keyundofile1.write( '\t%s\t%f\t%f\n'%('probA', oldProbA1, newProbA1) )
        keyundofile1.write( '\t%s\t%f\t%f\n'%('probB', oldProbB1, newProbB1) )
        
        keyundofile2.write( '\t%s\t%f\t%f\n'%('probA', oldProbA2, newProbA2) )
        keyundofile2.write( '\t%s\t%f\t%f\n'%('probB', oldProbB2, newProbB2) )
        
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distA', oldDistA1, newDistA1) )
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distB', oldDistB1, newDistB1) )
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB1, newDistAB1) )
        
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distA', oldDistA2, newDistA2) )
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distB', oldDistB2, newDistB2) )
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB2, newDistAB2) )
        
        keyundofile1.write( '\t%s\t%d\t%d\n'%('correctedPosA', oldCorrectedPosA1, newCorrectedPosA1) )
        keyundofile1.write( '\t%s\t%d\t%d\n'%('correctedPosB', oldCorrectedPosB1, newCorrectedPosB1) )
        
        keyundofile2.write( '\t%s\t%d\t%d\n'%('correctedPosA', oldCorrectedPosA2, newCorrectedPosA2) )
        keyundofile2.write( '\t%s\t%d\t%d\n'%('correctedPosB', oldCorrectedPosB2, newCorrectedPosB2) )
        
        keyundofile1.close()
        keyundofile2.close()
    
    def removeSVM(self, key):
        
        # Read pair keys
        off1, read_data1, spk_data1 = recogdb.readHeaderEntry(self.db, key)
        
        key1 = off1
        key2 = read_data1[ recogdb.dicFields['pairsvm'] ]
        
        off2, read_data2, spk_data2 = recogdb.readHeaderEntry(self.db, key2)
        
        # Open undo files
        if key1 not in self.undoKeys:
            undoFile1 = open(self.undoFilename, 'a')
            undoFile1.write('%s\n'%key1)
            undoFile1.flush()
            undoFile1.close()
        keyundofile1 = open(self.folder + '/' + str(key1) + '.undo', 'a')
        
        if key2 not in self.undoKeys:
            undoFile2 = open(self.undoFilename, 'a')
            undoFile2.write('%s\n'%key2)
            undoFile2.flush()
            undoFile2.close()
        keyundofile2 = open(self.folder + '/' + str(key2) + '.undo', 'a')
        
        # Read old data
        presentFish1 = read_data1[ recogdb.dicFields['presentFish'] ]
        presentFish2 = read_data2[ recogdb.dicFields['presentFish'] ]
        
        oldSVM1 = read_data1[ recogdb.dicFields['svm'] ]
        oldSVM2 = read_data2[ recogdb.dicFields['svm'] ]
        
        oldDistA1 = read_data1[ recogdb.dicFields['distA'] ]
        oldDistB1 = read_data1[ recogdb.dicFields['distB'] ]
        oldDistAB1 = read_data1[ recogdb.dicFields['distAB'] ]
        
        oldDistA2 = read_data2[ recogdb.dicFields['distA'] ]
        oldDistB2 = read_data2[ recogdb.dicFields['distB'] ]
        oldDistAB2 = read_data2[ recogdb.dicFields['distAB'] ]
        
        newSVM1 = 'm'
        newSVM2 = 'm'
        
        assert presentFish1 in [1, 2]
        if presentFish1 == 1:
            newDistA1 = 0
            newDistB1 = float('Inf')
            newDistAB1 = float('Inf')
        else:
            newDistA1 = float('Inf')
            newDistB1 = 0
            newDistAB1 = float('Inf')
        
        assert presentFish2 in [1, 2]
        if presentFish2 == 1:
            newDistA2 = 0
            newDistB2 = float('Inf')
            newDistAB2 = float('Inf')
        else:
            newDistA2 = float('Inf')
            newDistB2 = 0
            newDistAB2 = float('Inf')
        
        recogdb.updateHeaderEntry(self.db, key1, 'svm', newSVM1, sync=False)
        recogdb.updateHeaderEntry(self.db, key2, 'svm', newSVM2, sync=False)
        
        recogdb.updateHeaderEntry(self.db, key1, 'distA', newDistA1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key1, 'distB', newDistB1, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key1, 'distAB', newDistAB1, sync=False, change_svm=False)
        
        recogdb.updateHeaderEntry(self.db, key2, 'distA', newDistA2, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'distB', newDistB2, sync=False, change_svm=False)
        recogdb.updateHeaderEntry(self.db, key2, 'distAB', newDistAB2, sync=True, change_svm=False)
        
        # Read new data
        off1, new_data1, spk_data1 = recogdb.readHeaderEntry(self.db, key1)
        off2, new_data2, spk_data2 = recogdb.readHeaderEntry(self.db, key2)
        
        newSVM1 = new_data1[ recogdb.dicFields['svm'] ]
        newSVM2 = new_data2[ recogdb.dicFields['svm'] ]
        
        newDistA1 = new_data1[ recogdb.dicFields['distA'] ]
        newDistB1 = new_data1[ recogdb.dicFields['distB'] ]
        newDistAB1 = new_data1[ recogdb.dicFields['distAB'] ]
        
        newDistA2 = new_data2[ recogdb.dicFields['distA'] ]
        newDistB2 = new_data2[ recogdb.dicFields['distB'] ]
        newDistAB2 = new_data2[ recogdb.dicFields['distAB'] ]
        
        # Action identifier
        hashUndo = random.randint(0, 2**64-1)
        keyundofile1.write( '%s\t%d\n'%(dicUndo[SVMREMOVE], hashUndo) )
        keyundofile2.write( '%s\t%d\n'%(dicUndo[SVMREMOVE], hashUndo) )
        
        # Modified Fields
        keyundofile1.write( '\t%s\t%c\t%c\n'%('svm', oldSVM1, newSVM1) )
        keyundofile2.write( '\t%s\t%c\t%c\n'%('svm', oldSVM2, newSVM2) )
        
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distA', oldDistA1, newDistA1) )
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distB', oldDistB1, newDistB1) )
        keyundofile1.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB1, newDistAB1) )
        
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distA', oldDistA2, newDistA2) )
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distB', oldDistB2, newDistB2) )
        keyundofile2.write( '\t%s\t%f\t%f\n'%('distAB', oldDistAB2, newDistAB2) )
        
        keyundofile1.close()
        keyundofile2.close()
    
    
    def undo(self, modList, selected, key):
        # When the 'selected' is an action, he will look in the list for the first
        # action that matches
        
        if type(selected) is tuple:
            selectedAction, selectedHash = selected
            hashUndo = None
            action = None
            selected = -1 # Overwrites selected to a number, like the common usage
            while hashUndo != selectedHash:
                selected = selected + 1
                action, dicActions, hashUndo = modList[selected]
        else:
            action, dicActions, hashUndo = modList[selected]
            
            
        # Read to return if is a created SVM pair to be undone
        off, data, spkwin = recogdb.readHeaderEntry(self.db,key)
        pair_svm = data[ recogdb.dicFields['pairsvm'] ]
            
        if action not in [ dicUndo[RECOGFUTURE], dicUndo[RECOGPAST] ]:
            
            # Undo DB modifications 
            for field in dicActions.keys():
                assert dicFields[field] in ('int', 'float', 'char')
                if dicFields[field] == 'int':
                    data = int(dicActions[field][0])
                elif dicFields[field] == 'float':
                    data = float(dicActions[field][0])
                else:
                    data = dicActions[field][0]
                recogdb.updateHeaderEntry(self.db, key, field, data, sync=False, change_svm=False)
            self.db.sync()
            newModList = modList[selected+1:]
            self.regenUndoFile(key,newModList)
            
            offN = None
            offP = None
            if action in [ dicUndo[CREATESVM], dicUndo[SVMINVERTION] ]:
                offN, read_dataN = recogdb.getNearestSVM(self.db, 1, key)
                offP, read_dataP = recogdb.getNearestSVM(self.db, -1, key)
            
        else:
            
            offN, read_dataN = recogdb.getNearestSVM(self.db, 1, key)
            offP, read_dataP = recogdb.getNearestSVM(self.db, -1, key)
            
            modList.pop(selected)
            self.regenUndoFile(key, modList)
            
        return (action, offP, offN, pair_svm, hashUndo)


class IPIWindow(QtGui.QDialog):
    RButSize = 30
    RUndoLabelSize = 100
    RUndoStep = 140

    def __init__(self, db, undoFilename, folder, datafile):
        QtGui.QWidget.__init__(self)
        self.uiObject = Ui_IPIClick()
        self.uiObject.setupUi(self)
        
        self.db = db
        
        self.modify = ModifySelector(db, undoFilename, folder, datafile)

        QtCore.QObject.connect(self.uiObject.okButton, QtCore.SIGNAL('clicked()'), self.okClicked)
        QtCore.QObject.connect(self.uiObject.cancelButton, QtCore.SIGNAL('clicked()'), self.close)
        QtCore.QObject.connect(self.uiObject.undoButton, QtCore.SIGNAL('clicked()'), self.undoClicked)
        
        self.replot=False
        self.iterate_from = []

        self.move(0,0)

        self.options = []
        
        self.undoOptions = []
    
    def pop_iterate_from(self):
        return self.iterate_from.pop()

    def okClicked(self):
        option = -1
        for n,opt in enumerate(self.options):
            if opt.isChecked() == True:
                option = n
                break
        if option == -1:
            self.close()
        
        if self.windowType == 'continuity':
            # Invert fish
            if option == 0:
                self.modify.invertIPI(self.off)
                self.replot = True
            # Convert to overlap
            elif option == 1:
                self.hide()
                self.modify.convert2overlap(self.off)
                if self.modify.single2overlapWindow.replot == True:
                    self.replot = True
                    self.modify.single2overlapWindow.replot = False
                self.show()
            # Create SVM Pair
            elif option == 2:
                self.hide()
                self.modify.createSVMPair(self.off)
                if self.modify.replot == True:
                    self.replot = True
                    
                    msgbox = QtGui.QMessageBox()
                    msgbox.setText('Enforce SVM detection in direction:\n' + \
                    '(The detection will be done to the other side, but will respect the minimun distance)\n' + \
                    'WARNING: This may undo some of your manual modifications')
                    
                    msgbox.addButton(QtGui.QPushButton('Backward'), QtGui.QMessageBox.NoRole)
                    msgbox.addButton(QtGui.QPushButton('Foreward'), QtGui.QMessageBox.YesRole)
                    msgbox.addButton(QtGui.QPushButton('Both'), QtGui.QMessageBox.AcceptRole)
                    msgbox.addButton(QtGui.QPushButton('None'), QtGui.QMessageBox.AcceptRole)
                    
                    ret = msgbox.exec_()
                    
                    if ret == QtGui.QMessageBox.Cancel:
                        return None
                    
                    if ret == 0:
                        self.iterate_from.append( (1, False, self.off) )
                        self.iterate_from.append( (-1, True, self.off) )
                    if ret == 1:
                        self.iterate_from.append( (-1, False, self.off) )
                        self.iterate_from.append( (1, True, self.off) )
                    if ret == 2:
                        self.iterate_from.append( (1, True, self.off) )
                        self.iterate_from.append( (-1, True, self.off) )
                    if ret == 3:
                        self.iterate_from.append( (1, False, self.off) )
                        self.iterate_from.append( (-1, False, self.off) )
                        
                self.show()
            
        elif self.windowType == 'overlap':
            # Convert to single A
            if option == 0:
                self.modify.overlap2single(self.off, 'A')
                self.replot = True
            # Convert to single B
            elif option == 1:
                self.modify.overlap2single(self.off, 'B')
                self.replot = True
            # Change overlapping spike position
            elif option == 2:
                self.hide()
                self.modify.convert2overlap(self.off)
                if self.modify.single2overlapWindow.replot == True:
                    self.replot = True
                    self.modify.single2overlapWindow.replot = False
                self.show()
            
        elif self.windowType == 'svm':
            # Invert SVM
            if option == 0:
                self.modify.invertSVM(self.off)
                self.replot=True
                self.iterate_from.append( (1, True, self.off) )
                self.iterate_from.append( (-1, True, self.off) )
            # Remove SVM
            elif option == 1:
                self.modify.removeSVM(self.off)
                self.replot=True
                offN, dataN = recogdb.getNearestSVM(self.db, 1, self.off)
                offP, dataP = recogdb.getNearestSVM(self.db, -1, self.off)
                assert (offP is not None) or (offN is not None)
                if (offP is not None) and (offN is not None):
                    self.iterate_from.append( (1, False, offP) )
                    self.iterate_from.append( (-1, True, offN) )
                elif offP is None:
                    self.iterate_from.append( (-1, True, offN) )
                elif offN is None:
                    self.iterate_from.append( (1, True, offP) )
                
            # Reapply continuity (recog iterate_from)
            elif option == 2:
                
                self.replot = True
                
                key1, read_data1, spk_data1 = recogdb.readHeaderEntry(self.db, self.off)
                assert (read_data1[ recogdb.dicFields['svm'] ] in ['s', 'v'])
                off2 = read_data1[ recogdb.dicFields['pairsvm'] ]
                key2, read_data2, spk_data2 = recogdb.readHeaderEntry(self.db, off2)
                
                # Open undo file
                if key1 not in self.modify.undoKeys:
                    undoFile1 = open(self.modify.undoFilename, 'a')
                    undoFile1.write('%s\n'%key1)
                    undoFile1.flush()
                    undoFile1.close()
                keyundofile1 = open(self.modify.folder + '/' + str(key1) + '.undo', 'a')
                
                if key2 not in self.modify.undoKeys:
                    undoFile2 = open(self.modify.undoFilename, 'a')
                    undoFile2.write('%s\n'%key1)
                    undoFile2.flush()
                    undoFile2.close()
                keyundofile2 = open(self.modify.folder + '/' + str(key2) + '.undo', 'a')
                
                # Message box to ask future or past
                msgbox = QtGui.QMessageBox()
                msgbox.setText('Apply continuity criteria to: ')
                
                returnValues = [-1, 1]
                action = [ dicUndo[RECOGPAST], dicUndo[RECOGFUTURE] ]
                msgbox.addButton(QtGui.QPushButton('Past'), QtGui.QMessageBox.NoRole)
                msgbox.addButton(QtGui.QMessageBox.Cancel)
                msgbox.addButton(QtGui.QPushButton('Future'), QtGui.QMessageBox.YesRole)
                
                ret = msgbox.exec_()
                
                if ret == QtGui.QMessageBox.Cancel:
                    return None
                
                msgbox = QtGui.QMessageBox()
                msgbox.setText('Enforce?\n' + \
                'WARNING: This may undo some of your manual modifications')
                msgbox.addButton(QtGui.QMessageBox.Yes)
                msgbox.addButton(QtGui.QMessageBox.No)
                msgbox.addButton(QtGui.QMessageBox.Cancel)
                
                ret2 = msgbox.exec_()
                
                if ret2 == QtGui.QMessageBox.Cancel:
                    return None
                
                if ret2 == QtGui.QMessageBox.Yes:
                    enforce = True
                elif ret2 == QtGui.QMessageBox.No:
                    enforce = False
                
                # Apply iterate from
                self.iterate_from.append( (returnValues[ret], enforce, self.off) )
                
                # Modification file
                hashUndo = random.randint(0, 2**64-1)
                keyundofile1.write( '%s\t%d\n'%(action[ret], hashUndo) )
                keyundofile2.write( '%s\t%d\n'%(action[ret], hashUndo) )
                
                keyundofile1.close()
                keyundofile2.close()
                
        
        self.close()
    
    def undoClicked(self):
        option = -1
        for n,opt in enumerate(self.undoOptions):
            but, label = opt
            if but.isChecked() == True:
                option = n
                break
        if option == -1:
            self.close()
            return
        
        action, offP, offN, pair_svm, hashUndo = self.modify.undo(self.modList, option, self.off)
        if action == dicUndo[CREATESVM]:
            # When the option is an action, he will look in the list for the first
            # action that matches
            pairModList = self.modify.parseModifications(pair_svm)
            action, offP, offN, pair_svm, hashUndo = self.modify.undo(pairModList, (action, hashUndo), pair_svm)
            assert (offP is not None) or (offN is not None)
            if (offN is not None) and (offP is not None):
                self.iterate_from.append( (-1, False, offN) )
                self.iterate_from.append( (1, False, offP) )
                
            elif offP is None:
                self.iterate_from.append( (-1, False, offN) )
                
            elif offN is None:
                self.iterate_from.append( (1, False, offP) )
            
        elif action in [ dicUndo[SVMINVERTION], dicUndo[SVMREMOVE] ]:
            pairModList = self.modify.parseModifications(pair_svm)
            action, offP, offN, pair_svm, hashUndo = self.modify.undo(pairModList, (action, hashUndo), pair_svm)
            assert (offP is not None) or (offN is not None)
            if (offN is not None) and (offP is not None):
                self.iterate_from.append( (-1, False, offN) )
                self.iterate_from.append( (1, True, self.off) )
                
                self.iterate_from.append( (-1, False, self.off) )
                self.iterate_from.append( (1, True, offP) )
                
            elif offP is None:
                self.iterate_from.append( (-1, True, offN) )
                
            elif offN is None:
                self.iterate_from.append( (1, True, offP) )
        
        elif action == dicUndo[RECOGFUTURE]:
            pairModList = self.modify.parseModifications(pair_svm)
            action, offP, offN, pair_svm, hashUndo = self.modify.undo(pairModList, (action, hashUndo), pair_svm)
            if offN is not None:
                self.iterate_from.append( (-1, False, offN) )
            else:
                pass
        
        elif action == dicUndo[RECOGPAST]:
            pairModList = self.modify.parseModifications(pair_svm)
            action, offP, offN, pair_svm, hashUndo = self.modify.undo(pairModList, (action, hashUndo), pair_svm)
            if offP is not None:
                self.iterate_from.append( (1, False, offP) )
            else:
                pass
        
        self.replot = True
        self.close()
    
    def createMainOptions(self,text):
        self.uiObject.mainOptionsBox = QtGui.QGroupBox(self.uiObject.gridLayoutWidget)
        self.uiObject.mainOptionsBox.setObjectName(_fromUtf8("MainOptionsBox"))
        self.uiObject.mainOptionsLayout.addWidget(self.uiObject.mainOptionsBox, 0, 0, 1, 1)
        self.uiObject.mainOptionsBox.deleteLater()
        self.setGroupBoxTitle(text)

    def fillTextBoxes(self, Parameters):
        self.off = Parameters[2]
        
        parText = self.generateParameterText(Parameters)
        self.setParameterText(parText)
        self.createMainOptions('Options: ')
        self.fillMainOptions(Parameters)
        
        self.modList = self.modify.parseModifications(self.off)
        self.fillUndoOptions(self.modList)

    def fillUndoOptions(self, modList):
        if modList is None:
            return
        
        self.undoOptions = []
        i = 0
        for action, dicActions, hashUndo in modList:
            RadioBut =  QtGui.QRadioButton(self.uiObject.scrollAreaWidgetContents)
            RadioBut.setObjectName(_fromUtf8('undo' + str(i)))
            RadioBut.setMinimumHeight(self.RButSize)
            self.uiObject.verticalLayout.addWidget(RadioBut)
            RadioBut.deleteLater()
            
            Label = QtGui.QLabel(self.uiObject.scrollAreaWidgetContents)
            Label.setObjectName(_fromUtf8('undolabel' + str(i)))
            Label.setMinimumHeight(self.RUndoLabelSize)
            self.uiObject.verticalLayout.addWidget(Label)
            Label.deleteLater()
            
            font = QtGui.QFont()
            font.setFamily(_fromUtf8('Arial'))
            font.setPointSize(8)
            Label.setFont(font)
            
            self.undoOptions.append( (RadioBut, Label) )
            
            LabelText = ''
            for k in dicActions.iterkeys():
                LabelText = LabelText + k + ': ' + str(dicActions[k][0]) + ' -> ' + str(dicActions[k][1]) + '\n'
            
            self.setUndoOpt(i, action.strip(), LabelText)
            
            i = i + 1

    def fillMainOptions(self, Parameters):

        self.svm = Parameters[4]

        self.options = []

        # single continuity spike
        '''if self.svm not in ['s', 'v']:'''
        if self.fish != 3:
            self.windowType = 'continuity'
            self.setMainText('Continuity spike selected')

            for i in xrange(3):
                self.options.append( QtGui.QRadioButton(self.uiObject.mainOptionsBox) )
                self.options[-1].setGeometry(QtCore.QRect(0, self.RButSize*(1+i), 300, self.RButSize))
                self.options[-1].setObjectName(_fromUtf8('opt' + str(i)))

            self.setOpt(0, 'Invert fish classification')
            self.setOpt(1, 'Convert to overlapping spike')
            self.setOpt(2, 'Create SVM Pair')

        # Overlapping spike
        else:
            self.windowType = 'overlap'
            self.setMainText('Overlapping spikes selected')

            for i in xrange(3):
                self.options.append( QtGui.QRadioButton(self.uiObject.mainOptionsBox) )
                self.options[-1].setGeometry(QtCore.QRect(0, self.RButSize*(1+i), 300, self.RButSize))
                self.options[-1].setObjectName(_fromUtf8('opt' + str(i)))

            self.setOpt(0, 'Convert to single A spike')
            self.setOpt(1, 'Convert to single B spike')
            self.setOpt(2, 'Change spike positioning')

        '''# SVM spike
        else:
            self.windowType = 'svm'
            self.setMainText('SVM spike selected')

            for i in xrange(3):
                self.options.append( QtGui.QRadioButton(self.uiObject.mainOptionsBox) )
                self.options[-1].setGeometry(QtCore.QRect(0, self.RButSize*(1+i), 300, self.RButSize))
                self.options[-1].setObjectName(_fromUtf8('opt' + str(i)))

            self.setOpt(0, 'Invert SVM classification')
            self.setOpt(1, 'Remove SVM classification')
            self.setOpt(2, 'Recalculate continuity from this SVM')'''

    def parseSVMFlag(self,svmFlag):
        if svmFlag == 'a':
            return 'Spike has to much samples'
        elif svmFlag == 'd':
            return 'Interval between spikes (any fish) is too long'
        elif svmFlag == 'm':
            return 'Manually modificated'
        elif svmFlag == 'i':
            return 'Insufficient good channels'
        elif svmFlag == 'o':
            return 'Overlapping spikes'
        elif svmFlag == 'p':
            return 'Probability below minimum'
        elif svmFlag == 'w':
            return 'No pair detected'
        elif svmFlag == 's':
            return 'SVM Classified'
        elif svmFlag == 'v':
            return 'Manually inserted or inverted SVM'
        elif svmFlag == 'c':
            return 'Previous spike was not ready for SVM classification'

    def generateParameterText(self,Par):
        self.fish = Par[0]
        if self.fish == 1:
            fishtxt = 'Fish A'
        elif self.fish == 2:
            fishtxt = 'Fish B'
        elif self.fish == 3:
            fishtxt = 'Both A + B'
        text = '' + \
            'fish: ' + '\n' + \
            str(fishtxt) + '\n\n' + \
            'Timestamp: ' + '\n' + \
            str(Par[1]) + '\n\n' + \
            'offset on .memmapf32 file (bytes): ' + '\n' + \
            str(Par[2]) + '\n\n' + \
            'direction: ' + '\n' + \
            str(Par[3]) + '\n\n' + \
            'SVM status: ' + '\n' + \
            str(self.parseSVMFlag(Par[4])) + '\n\n' + \
            'Probability for A: ' + '\n' + \
            str(Par[5]) + '\n\n' + \
            'Probability for B: ' + '\n' + \
            str(Par[6]) + '\n\n' + \
            'Euclidean distance from last single A: ' + '\n' + \
            str(Par[7]) + '\n\n' + \
            'Euclidean distance from last single B: ' + '\n' + \
            str(Par[8]) + '\n\n' + \
            'Euclidean distance from overlapping last single A and last single B: ' + '\n' + \
            str(Par[9]) + '\n\n'
        return text

    def setMainText(self, text):
        self.uiObject.mainText.setText(_translate("IPIClick", text, None))

    def setParameterText(self, text):
        self.uiObject.parameters.setText(_translate("IPIClick", text, None))

    def setGroupBoxTitle(self, text):
        self.uiObject.mainOptionsBox.setTitle(_translate("IPIClick", text, None))

    def setOpt(self, num, text):
        self.options[num].setText(_translate("IPIClick", text, None))

    def setUndoOpt(self,num, textRadio, textLabel):
        self.undoOptions[num][0].setText(_translate("IPIClick", textRadio, None))
        self.undoOptions[num][1].setText(_translate("IPIClick", textLabel, None))
