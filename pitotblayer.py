

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox, QDialogButtonBox, QDialog)

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


from wrobolib.roboclient import RoboClient

import scanigui
import pitotgui


class RoboIP(QDialog):

    def __init__(self, ip='localhost', port=9595, *args, **kwargs):

        super(RoboIP, self).__init__(*args, **kwargs)

        self.setWindowTitle('Servidor XML-RPC do robo')

        self.draw_gui(ip, port)
        
    def draw_gui(self, ip='', port=9595):

        self.server = QGroupBox('Servidor XML-RPC do Robo')
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
       

        vb.addLayout(hb1)
        vb.addLayout(hb2)
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        vb.addWidget(self.buttonBox)
        self.setLayout(vb)
        
        return
    def url(self):
        ip = self.iptext.text().strip()
        port = int(self.porttext.text())

        return ip, port
        
    
class PitotBLayer(QMainWindow):
    """
    Interface para especificação de movimento 1D
    """

    def __init__(self, parent=None):

        
        super(BLayer, self).__init__(parent)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)


        self.mov = None
        self.scaniwin = None
        self.pts = None
        self.pitot = None
        
        chans = ["Canal {}".format(i) for i in range(17)]
        chans[0] = "REF"
        self.chans = pitotgui.ChannelConfig(chans)
        
        hb = QHBoxLayout()
        vb1 = QVBoxLayout()
        vb2 = QVBoxLayout()


        menubar = self.menuBar()
        menuarq = menubar.addMenu("&Arquivo")
        

        menuarq
        menusair = menubar.addMenu("&Sair")
        
        
        grp0 = QGroupBox("Configurar movimentação")
        self.url = 'localhost', 9595
        buttonRobo = QPushButton("Configurar Robo")
        vb2.addWidget(buttonRobo)
        buttonRobo.clicked.connect(self.conectar_robo)
        
        

        self.ptsbutton = QPushButton("Definição dos pontos de medição")
        self.ptsbutton.clicked.connect(self.def_points)
        vb2.addWidget(self.ptsbutton)

        grp0.setLayout(vb2)
        vb1.addWidget(grp0)
        

        grp1 = QGroupBox("Configurar aquisição de dados")
        vb3 = QVBoxLayout()
        self.scanibut = QPushButton("Configurar Scanivalve")
        self.scanibut.setToolTip("Configurar e conectar com o scanivalve")
        self.scanibut.clicked.connect(self.scani_config)
        vb3.addWidget(self.scanibut)

        self.pitotbut = QPushButton("Configuras os tubos de Pitot")
        self.pitotbut.setToolTip("Configurar os tubos de Pitot e tomadas de pressão do Scanivalve")
        self.pitotbut.clicked.connect(self.pitot_config)
        vb3.addWidget(self.pitotbut)

        grp1.setLayout(vb3)
        vb1.addWidget(grp1)

        self.measbutton = QPushButton("Realizar Medições")
        self.measbutton.setEnabled(False)
        self.measbutton.clicked.connect(self.measure)

        vb1.addWidget(self.measbutton)
        
        
        hb.addLayout(vb1)

        self.widget.setLayout(hb)
        self.setWindowTitle('Camada Limite com Pitot')

        #self.ptswin = pos1d.Pos1dWindow()

    def all_ready(self):

        if self.ptswin is not None and self.scaniwin is not None and self.pitotwin is not None:
            return True
        else:
            return False
        
    def robo(self):
        if self.mov is not None:
            return self.mov
        else:
            return None
    def scanivalve(self):
        if self.scaniwin is not None:
            return self.scaniwin.scanivalve()
        else:
            return None
    def points(self):
        if self.ptswin is not None:
            return self.ptswin.getpoints()
        else:
            return None
    def pitot(self):
        if self.pitotwin is not None:
            return self.pitotwin.config()
        else:
            return None
        

        
        
    def conectar_robo(self):
        ip, port = self.url

        mov = self.roboconnect(ip, port)
        if mov is not None:
            self.mov = mov
        return

    def roboconnect(self, ip, port):

        if self.mov is not None:
            ans = QMessageBox.information(self, 'Robô já está conectado',
                                          'Se a conexão estiver boa deseja continuar utilizando-a?',
                                          QMessageBox.Yes | QMessageBox.No)
            if ans == QMessageBox.Yes:
                try:
                    if self.mov.ping() == 123:
                        return self.mov
                    else:
                        raise RuntimeError("Não conectou")
                except:
                    pass

        dlg = RoboIP(ip, port)
        if dlg.exec_():
            ntries = 3
            wait = 3
            mov = RoboClient()
            err = False
            for i in range(ntries):
                mysleep(wait)
                print('Tentando conectar...')
                success = mov.connect(ip, port)
                if success:
                    QMessageBox.information(self, 'Conexão com o Robo bem sucedida',
                                            "Conectado ao servidor XML-RPC do robo em http://{}:{}".format(ip, port), QMessageBox.Ok)
                    return mov
                else:
                    err = True
            QMessageBox.critical(self, 'Erro conectando ao servidor XML-RPC',
                                 "Inicie o servidor de XML-RPC do robô ou mude o IP/Porta",
                                 QMessageBox.Ok)
        return None
    
        
    def def_points(self):
        if self.ptswin is None:
            self.ptswin = pos1d.Pos1dWindow(parent=self)

        if self.all_ready():
            self.measbutton.setEnabled(True)
            
        self.ptswin.show()
        
    def scani_config(self):
        if self.scaniwin is None:
            self.scaniwin = scanigui.ScaniWin(parent=self)

        if self.all_ready():
            self.measbutton.setEnabled(True)

        self.scaniwin.show()
    def pitot_config(self):
        if self.pitotwin is None:
            self.pitotwin = pitotgui.PitotWin(self.chans, parent=self)

        if self.all_ready():
            self.measbutton.setEnabled(True)

        self.pitotwin.show()
    def measure(self):
        pass
        

class PitotMeasWin(QMainWindow):

    def __init__(self, robo, points, scani, pitot):
        super(PitotMeasWin, self).__init__(parent)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.scani = None
        pass
    
    

if __name__ == '__main__':
    app = QApplication([])

    win = BLayer()#'192.168.0.101')

    win.show()

    #sys.exit(app.exec_())
    app.exec_()

    print(win.points())
          
    #print(win.getpoints())
    
