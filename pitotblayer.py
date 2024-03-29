

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox, QDialogButtonBox, QDialog,
                             QRadioButton, QListWidget)

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
import channels



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

ch = '✓'

class WindTunnelTest(QWidget):

    def __init__(self, ptslst, parent=None):
        super(WindTunnelTest, self).__init__(parent)
        self.ptslst = ptslst
        hb = QHBoxLayout()
        self.active_section = 0
        self.change_section = True
        grp1 = self.setup_ptslst(ptslst)

        hb.addWidget(grp1)
        self.setLayout(hb)
        return
    
    def setup_ptslst(self, ptslst):

        grp = QGroupBox("Pontos de medição")
        vb = QVBoxLayout()

        nsecs = len(ptslst)
        secnames = ["Parte {}".format(i+1) for i in range(nsecs)]
        self.radio = [QRadioButton(s) for s in secnames]
        for i in range(nsecs):
            self.radio[i].section = i
            self.radio[i].toggled.connect(self.onClicked)
        self.text = [QListWidget(self) for i in range(nsecs)]
        self.radio[self.active_section].setChecked(True)
        for i in range(nsecs):
            t = self.text[i]
            for s in range(ptslst[i]):
                t.addItem('Ponto {}'.format(s+1))

        for i in range(nsecs):
            vb.addWidget(self.radio[i])
            vb.addWidget(self.text[i])
            self.text[i].setVisible(False)


        self.text[self.active_section].setVisible(True)
        
        
        grp.setLayout(vb)
        return grp
    def onClicked(self):
        r = self.sender()
        i = r.section
        self.text[self.active_section].setVisible(False)
        self.text[i].setVisible(True)
        self.active_section = i
        self.change_section = True
        
        
    def setup_meas(self):
        pass
        
            
class PitotBLayerWin(QMainWindow):
    """
    Interface para especificação de movimento 1D
    """

    def __init__(self, parent=None):

        
        super(PitotBLayerWin, self).__init__(parent)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.setWindowTitle('Camada Limite com Pitot')
        

        
        self.chans = channels.ChannelConfig(16, addref=True, istart=1)
        
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
        measAct.setEnabled(False)
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
                    self.all_ready()
                    return
                else:
                    err = True
                    
            QMessageBox.critical(self, 'Erro conectando ao servidor XML-RPC',
                                 "Inicie o servidor de XML-RPC do robô ou mude o IP/Porta",
                                 QMessageBox.Ok)
            self.setEnabled(True)
            self.robo = None
            self.menu['measure'].setEnabled(False)
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
            self.menu['measure'].setEnabled(False)

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
        self.all_ready()
            
    def menu_scanivalve(self):
        if self.scaniwin is None:
            self.scaniwin = scanigui.ScaniWin(parent=self)
        self.scaniwin.show()
        self.all_ready()
        
    def menu_pitot(self):
        if self.pitot is not None:
            dlg = pitotgui.PitotConfig(self.chans, self.pitot, self)
        else:
            dlg = pitotgui.PitotConfig(self.chans, parent=self)

        ans = dlg.exec_()

        if ans:
            self.pitot = dlg.save_config()
        self.all_ready()
        

    def menu_measure(self):
        print('MEDIR!!!')
        
    def all_ready(self):
        x = self.pos is not None
        r = self.robo is not None
        s = self.scaniwin is not None and self.scaniwin.connected()
        p = self.pitot is not None

        if x and r and s and p:
            self.menu['measure'].setEnabled(True)
            return True
        else:
            self.menu['measure'].setEnabled(False)
            return False
        
        
class PitotMeasWidget(QWidget):

    def __init__(self, parent=None):
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

    #win = PitotBLayerWin()#'192.168.0.101')
    win = WindTunnelTest([30, 20, 10, 5])
    win.show()

    app.exec_()

    
