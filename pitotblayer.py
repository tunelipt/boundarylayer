

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
from wrobolib import pyqtrobo



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
        
            
class PitotBLayerWin(QMainWindow):
    """
    Interface para especificação de movimento 1D
    """

    def __init__(self, parent=None):

        
        super(PitotBLayerWin, self).__init__(parent)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.setWindowTitle('Camada Limite com Pitot')
        

        
        chans = ["Canal {}".format(i) for i in range(17)]
        chans[0] = "REF"
        self.chans = pitotgui.ChannelConfig(chans)
        
        self.setup_ui()

        self.url = None
        self.robo = None
        self.robowin = None
        self.pos = None
        self.scaniwin = None
        self.pitot = None

        
    def setup_ui(self):

        
        menubar = self.menuBar()
        menufile = menubar.addMenu("&Arquivo")
        newAct = QAction("&Novo", self)
        newAct.setShortcut("Ctrl+N")
        newAct.setStatusTip("Nova medição de camada limite")
        newAct.triggered.connect(self.menu_new)
        menufile.addAction(newAct)

        saveAct = QAction('&Salvar', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.setStatusTip('Salvar dados de configuração e medição')
        saveAct.triggered.connect(self.menu_save)
        menufile.addAction(saveAct)
        menufile.addSeparator()


        exitAct = QAction('Sai&r', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Sair do programa')
        exitAct.triggered.connect(self.menu_exit)
        menufile.addAction(exitAct)

        menupos = menubar.addMenu("&Posição")

        rconnAct = QAction('&Conexão com robô', self)
        rconnAct.setStatusTip('Conectar ao servidor XML-RPC do robô')
        rconnAct.triggered.connect(self.menu_rconn)
        menupos.addAction(rconnAct)

        rdisconnAct = QAction('&Desconectar robô', self)
        rdisconnAct.setStatusTip('Desconectar da interface XML-RPC do robô')
        rdisconnAct.triggered.connect(self.menu_rdisconn)
        menupos.addAction(rdisconnAct)
        menupos.addSeparator()
        rdisconnAct.setEnabled(False)
        
        
        roboAct = QAction('Posicinar &robô', self)
        roboAct.setStatusTip('Interface para mover robô')
        roboAct.setShortcut('Ctrl+R')
        roboAct.triggered.connect(self.menu_robo)
        menupos.addAction(roboAct)
        roboAct.setEnabled(False)
        
        menupos.addSeparator()

        posAct = QAction('&Pontos de medição', self)
        posAct.setStatusTip('Definição dos pontos de medição')
        posAct.triggered.connect(self.menu_pos)
        menupos.addAction(posAct)
        
        menumeas = menubar.addMenu("&Medidas")

        scaniAct = QAction('&Scanivalve', self)
        #scaniAct.setShortcut('Ctrl+V')
        scaniAct.setStatusTip('Configurar e conectar ao Scanivalve')
        scaniAct.triggered.connect(self.menu_scanivalve)
        menumeas.addAction(scaniAct)

        pitotAct = QAction('&Configurar medições', self)
        #pitotAct.setShortcut('Ctrl+P')
        pitotAct.setStatusTip('Configurar canais e medições')
        pitotAct.triggered.connect(self.menu_pitot)
        menumeas.addAction(pitotAct)
        
        menumeas.addSeparator()

        measAct = QAction('&Medir!', self)
        measAct.setShortcut('Ctrl+M')
        measAct.setStatusTip('Realizar o ensaio')
        measAct.triggered.connect(self.menu_measure)
        menumeas.addAction(measAct)
        
        self.menu = dict(new=newAct, save=saveAct, exit=exitAct,
                         rconn=rconnAct, rdisconn=rdisconnAct, robo=roboAct, pos=posAct,
                         scanivalve=scaniAct, pitot=pitotAct, measure=measAct)
        
        self.statusBar()
        

        hb = QHBoxLayout()

        self.widget.setLayout(hb)
        self.setWindowTitle('Camada Limite com Pitot')

    def menu_new(self):
        print("NOVO!")
    def menu_save(self):
        print('SALVAR')
    def menu_exit(self):
        print('SAIR')
    def menu_rconn(self):
        if self.url is not None:
            ip, port = self.url
        else:
            ip, port = 'localhost', 9595
        dlg = RoboIP(ip, port)
        if dlg.exec_():
            self.url = dlg.url()
            ip, port = self.url
            ntries = 3
            wait = 3
            robo = RoboClient()
            err = False
            self.setEnabled(False)
            for i in range(ntries):
                mysleep(wait)
                print('Tentando conectar...')
                success = robo.connect(ip, port)
                if success:
                    QMessageBox.information(self, 'Conexão com o Robo bem sucedida',
                                            "Conectado ao servidor XML-RPC do robo em http://{}:{}".format(ip, port), QMessageBox.Ok)
                    self.robo = robo
                    self.setEnabled(True)
                    self.menu['rconn'].setEnabled(False)
                    self.menu['rdisconn'].setEnabled(True)
                    self.menu['robo'].setEnabled(True)
                    return
                else:
                    err = True
                    
            QMessageBox.critical(self, 'Erro conectando ao servidor XML-RPC',
                                 "Inicie o servidor de XML-RPC do robô ou mude o IP/Porta",
                                 QMessageBox.Ok)
            self.setEnabled(True)
            self.robo = None
        return 
        
    def menu_rdisconn(self):
        ans = QMessageBox.information(self, 'Desconexão do robô',
                                      "Desconectar da interface XML-RPC do robô?",
                                      QMessageBox.Ok | QMessageBox.Cancel)
        if ans == QMessageBox.Ok:
            self.robo = None
            self.menu['rconn'].setEnabled(True)
            self.menu['rdisconn'].setEnabled(False)
            self.menu['robo'].setEnabled(False)

    def menu_robo(self):
        if self.robowin is not None:
            self.robowin.robo = self.robo
        else:
            self.robowin = pyqtrobo.RoboWindow(self.robo, 'Camada Limite', None, self)

        self.robowin.show()
        
    def menu_pos(self):
        if self.pos is not None:
            axis, points = self.pos
            secs = [p[2] for p in points]
        else:
            secs = pos1d.secsdefault
            axis = 'z'
        dlg = pos1d.Pos1dDialog(axis, secs, parent=self)
        ans = dlg.exec_()
        if ans:
            self.pos = dlg.getpoints()
            
    def menu_scanivalve(self):
        if self.scaniwin is None:
            self.scaniwin = scanigui.ScaniWin(parent=self)
        self.scaniwin.show()
        #if self.all_ready():
        #    self.measbutton.setEnabled(True)
        #print('Configurar scanivalve')
    def menu_pitot(self):
        if self.pitot is not None:
            dlg = pitotgui.PitotConfig(self.chans, self.pitot, self)
        else:
            dlg = pitotgui.PitotConfig(self.chans, parent=self)

        ans = dlg.exec_()

        if ans:
            self.pitot = dlg.config()

    def menu_measure(self):
        print('MEDIR!!!')
        
    def all_ready(self):

        if self.pos is not None and self.scaniwin is not None and self.pitotwin is not None:
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

    win = PitotBLayerWin()#'192.168.0.101')

    win.show()

    app.exec_()

    
