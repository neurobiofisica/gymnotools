from PyQt4 import QtGui, QtCore
import os, inspect, sys

def chooserDialog():
    dialog = QtGui.QMessageBox()
    dialog.setWindowTitle('Gymnotools')
    dialog.setText('Please choose train or discriminate mode:\n')
    dialog.setModal(True)
    dialog.addButton(QtGui.QPushButton('Train'), QtGui.QMessageBox.YesRole) #0
    dialog.addButton(QtGui.QPushButton('Discriminate'), QtGui.QMessageBox.NoRole) #1
    dialog.addButton(QtGui.QMessageBox.Close)
    
    ansDic = {0: 'train', \
              1: 'discriminate', \
             }
    
    ret = dialog.exec_()
    
    return ret, ansDic

if __name__ == '__main__':
    file_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    curr_dir = os.getcwd()
    
    if curr_dir != file_dir:
        os.chdir(file_dir)

    app = QtGui.QApplication(sys.argv)
    ret, ansDic = chooserDialog()
    
    if ret in ansDic:
        from gui import training, discriminate
        if ansDic[ret] == 'train':
            myapp = training.TrainingWindow(app)
        elif ansDic[ret] == 'discriminate':
            myapp = discriminate.DiscriminateWindow(app)
        
        myapp.show()
        sys.exit(app.exec_())