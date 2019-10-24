from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox)

from PyQt5.QtCore import Qt, QRegExp, QEventLoop, QTimer

from PyQt5.QtGui import QPixmap, QIcon, QRegExpValidator, QDoubleValidator, QIntValidator
import time



import scanivalve


class PitotWin(QMainWindow):


    def __init__(self, parent=None):

        super(PitotWin, self).__init__(parent)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.scani = None
        hb = QHBoxLayout()
        vb = QVBoxLayout()

        self.grip = QGroupBox("Scanivalve")
        vb1 = QVBoxLayout()
        hb1 = QHBoxLayout()
        hb1.addWidget(QLabel("IP"))
        self.iptext = QLineEdit("191.30.80.131")
        hb1.addWidget(self.iptext)
        vb1.addLayout(hb1)
        
        self.ipbut = QPushButton("Conectar")
        self.ipbut.clicked.connect(self.connect)

        vb1.addWidget(self.ipbut)
        
        self.grip.setLayout(vb1)

        vb.addWidget(self.grip)
        hb.addLayout(vb)
        
        self.widget.setLayout(hb)
        
        self.setWindowTitle('Configuração do Scanivalve')

    def configgui(self):
        pass
    
    def connect(self):
        try:
            ip = self.iptext.text()
            s = scani.Scanivalve(ip)
        except:
            pass
        
    

if __name__ == '__main__':
    app = QApplication([])

    win = PitotWin()

    win.show()

    #sys.exit(app.exec_())
    app.exec_()

    
        
