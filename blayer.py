

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox)

from PyQt5.QtCore import Qt, QRegExp, QEventLoop, QTimer

from PyQt5.QtGui import QPixmap, QIcon, QRegExpValidator, QDoubleValidator, QIntValidator
import time

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

import pos1d
import wrobolib.roboclient as roboclient


def mysleep(ns):
    loop = QEventLoop()
    QTimer.singleShot(ns*1000, loop.quit)
    loop.exec_()
    return None
    
class BLayer(QMainWindow):
    """
    Interface para especificação de movimento 1D
    """

    def __init__(self, parent=None):

        
        super(BLayer, self).__init__(parent)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)


        self.robo = None
        hb = QHBoxLayout()
        vb1 = QVBoxLayout()
        vb2 = QVBoxLayout()

        self.server = self.serverinfo('localhost', 9595)

        vb1.addWidget(self.server)

        self.ptsbutton = QPushButton("Definição dos pontos de medição")
        self.ptsbutton.clicked.connect(self.defpoints)
        vb1.addWidget(self.ptsbutton)
        
        self.ptswin = pos1d.Pos1dWindow(self)
        
        hb.addLayout(vb1)

        self.widget.setLayout(hb)
        self.setWindowTitle('Camada Limite')
        

        

        
        

    def serverinfo(self, ip='', port=9595):

        self.server = QGroupBox('Servidor XML-RPC')
        vb = QVBoxLayout()
        hb1 = QHBoxLayout()
        hb2 = QHBoxLayout()

        iplab = QLabel('IP')
        self.iptext = QLineEdit(ip)
        hb1.addWidget(iplab)
        hb1.addWidget(self.iptext)

        portlab = QLabel('Porta')
        self.porttext = QLineEdit(str(port))
        self.pvalid = QIntValidator(1, 65535)
        self.porttext.setValidator(self.pvalid)
        
        hb2.addWidget(portlab) 
        hb2.addWidget(self.porttext)
       

        self.connbut = QPushButton('Conectar')
        self.connbut.clicked.connect(self.connect_robo)

        vb.addLayout(hb1)
        vb.addLayout(hb2)
        vb.addWidget(self.connbut)

        self.server.setLayout(vb)

        return self.server
    def connect_robo(self):
        print("AQUI")
        ntries=3
        wait=3
        if self.robo is not None:
            self.connbut.setText('Conectar')
            self.robo = None
            return

        ip = self.iptext.text()
        port = self.porttext.text()

        self.robo = roboclient.RoboClient()
        err = False
        for i in range(ntries):
            mysleep(wait)
            print('Tentando conectar...')
            success = self.robo.connect(ip, port)
            
            if success:
                self.connbut.setText('Desconectar')
                return
            else:
                err = True
            
    
        QMessageBox.critical(self, 'Erro conectando ao servidor XML-RPC',
                             "Inicie o servidor de XML-RPC do robô ou mude o IP/Porta",
                             QMessageBox.Ok)
        
    def defpoints(self):
        self.ptswin.show()
        

if __name__ == '__main__':
    app = QApplication([])

    win = BLayer()#'192.168.0.101')

    win.show()

    #sys.exit(app.exec_())
    app.exec_()
    print(win.ptswin.getpoints())
    
    #print(win.getpoints())
    
