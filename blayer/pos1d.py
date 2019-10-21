

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QPixmap, QIcon, QRegExpValidator, QDoubleValidator, QIntValidator
import time

import positions as pos
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

        
class Pos1dWindow(QMainWindow):
    """
    Interface para especificação de movimento 1D
    """

    def __init__(self, ip='', port=9595, parent=None):

        super(Pos1dWindow, self).__init__(parent)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        hb = QHBoxLayout()
        
        vb = QVBoxLayout()
        
        self.ip = None
        self.port = None

        self.serverwin = self.serverinfo(ip, port)
        self.posgb = self.poswin()
        
        vb.addWidget(self.serverwin)
        vb.addWidget(self.posgb)
        hb.addLayout(vb)

        dpi = 100
        width=5
        height=4
        self.plt = QGroupBox("Verificação", width=width*100, height=height*dpi)
        vb1 = QVBoxLayout()
        
        self.plotwin = CheckPointsWindow(self, width, height, dpi)
        vb1.addWidget(self.plotwin)
        hb.addLayout(vb1)
        
        self.widget.setLayout(hb)
        self.setWindowTitle('Configurando Robo')
        

    def serverinfo(self, ip='', port=9596):

        self.server = QGroupBox('Servidor XML-RPC')
        vb = QVBoxLayout()
        hb1 = QHBoxLayout()
        hb2 = QHBoxLayout()

        iplab = QLabel('IP')
        self.iptext = QLineEdit(ip)
        hb1.addWidget(iplab)
        hb1.addWidget(self.iptext)

        portlab = QLabel('Porta')
        self.porttext = QLineEdit(str(self.port))
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
        self.connbut.setText('Desconectar')
        ip = self.iptext.getText()
        port = self.porttext.getText()

        try:
            port = int(port)
        except:
            println("ERRO")
        
        print("Conectar...")
        

    def poswin(self, axis='z', p=['10~580~35~1.05'], nsectot=3):

        self.nsectot = nsectot
        
        self.posgb = QGroupBox("Posições")
        vb = QVBoxLayout()
        hb1 = QHBoxLayout()
        hb2 = QHBoxLayout()

        hb3 = [QHBoxLayout() for i in range(nsectot)]

        eixolab = QLabel('Eixo')
        self.eixocb = QComboBox()
        self.eixocb.addItems(['x', 'y', 'z'])
        self.eixocb.setCurrentIndex(2)
        hb1.addWidget(eixolab)
        hb1.addWidget(self.eixocb)
        
        #seclab = QLabel("Número de seções")
        #self.seccb = QComboBox()
        #self.seccb.addItems([str(i+1) for i in range(nsectot)])
        #self.seccb.setCurrentIndex(0)
        #hb2.addWidget(seclab)
        #hb2.addWidget(self.seccb)

        poslab = [QLabel('Seção {}'.format(i+1)) for i in range(nsectot)]
        self.postext = [QLineEdit('') for i in range(nsectot)]

        if p is None:
            p = ['']
                   
        if not isinstance(p, (list, tuple)):
            p = [p]
        np = len(p)
        for i in range(np):
            self.postext[i].setText(p[i])
            
        for i in range(nsectot):
            hb3[i].addWidget(poslab[i])
            hb3[i].addWidget(self.postext[i])
        vb.addLayout(hb1)
        #vb.addLayout(hb2)
        for i in range(nsectot):
            vb.addLayout(hb3[i])


        self.posplotbut = QPushButton("Plotar os pontos")
        self.posplotbut.clicked.connect(self.checkpoints)
        
        self.sairbut = QPushButton("Sair")
        hb2.addWidget(self.posplotbut)
        hb2.addWidget(self.sairbut)
        vb.addLayout(hb2)
        
        self.posgb.setLayout(vb)
        return self.posgb
    
    def getpoints(self):
        points = []
        for i in range(self.nsectot):
            s = self.postext[i].text().strip()

            if s == '':
                break

            try:
                p = pos.parsenumlst(s)
                points.append((i, p))
            except:
                QMessageBox.critical(self, 'Erro interpretando os pontos', "Não foi possível entender o que {} quer dizer".format(s),  QMessageBox.Ok)
                return None
        return points
            
                
    

            
    def checkpoints(self):
        pts = self.getpoints()
        self.plotwin.draw_points(pts, self.eixocb.currentText())
        
        pass
        
    

class CheckPointsWindow(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

        return

    def draw_points(self, pts, ax='z'):
        self.axes.cla()
        nn = len(pts)
        if ax=='z':
            self.axes.set_xlabel('Velocidade')
            self.axes.set_ylabel('Altura {} (mm)'.format(ax))
        else:
            self.axes.set_xlabel('Posição {} (mm)'.format(ax))
            self.axes.set_ylabel('Velocidade')
            
        for i in range(nn):
            if ax=='z':
                isec = pts[i][0]
                p = np.array(pts[i][1])
                u = 10.0 * (p/500)**0.3
                self.axes.plot(u, p, color=self.colors[i], marker='o', linestyle='' ,
                               label='Seção {}'.format(isec+1))
            else: # ax=='x' ou 'y':
                isec = pts[i][0]
                p = np.array(pts[i][1])
                u = np.ones(len(pts[i][1]))
                self.axes.plot(p, u,  color=self.colors[i], marker='o', linestyle='' ,
                               label='Seção {}'.format(isec+1))
                            

        self.axes.legend()
            
        self.draw()
        return None
    
        
if __name__ == '__main__':
    app = QApplication([])

    win = Pos1dWindow('192.168.0.101')

    win.show()

    sys.exit(app.exec_())
    
