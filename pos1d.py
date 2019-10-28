

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox)
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

    def __init__(self, parent=None):

        super(Pos1dWindow, self).__init__(parent)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.is_ready = False
        
        hb = QHBoxLayout()
        
        vb = QVBoxLayout()
        
        self.posgb = self.poswin()
        
        vb.addWidget(self.posgb)
        self.sairbut = QPushButton("Sair")
        self.sairbut.clicked.connect(self.sair)        
        vb.addWidget(self.sairbut)
        hb.addLayout(vb)

        dpi = 100
        width=5
        height=4
        self.plt = QGroupBox("Verificação", width=width*100, height=height*dpi)
        vb1 = QVBoxLayout()
        
        self.plotwin = CheckPointsWindow(self, width, height, dpi)
        vb1.addWidget(self.plotwin)
        hb.addLayout(vb1)

        quit = QAction("Sair", self)
        quit.triggered.connect(self.sair)        
        self.widget.setLayout(hb)
        self.setWindowTitle('Configurando Robo')
        
        
    def isready(self):
        return self.is_ready
    
    def poswin(self, axis='z', p=['10~580~35~1.05'], nsectot=5):

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


        self.posplotbut = QPushButton("Definir os pontos")
        self.posplotbut.clicked.connect(self.checkpoints)
        
        hb2.addWidget(self.posplotbut)
        vb.addLayout(hb2)
        
        self.posgb.setLayout(vb)
        return self.posgb
    
    def getpoints(self):
        points = []
        for i in range(self.nsectot):
            s = self.postext[i].text().strip()

            if s == '':
                continue

            try:
                p = pos.parsenumlst(s)
                points.append((i, p))
            except:
                QMessageBox.critical(self, 'Erro interpretando os pontos', "Não foi possível entender o que {} quer dizer".format(s),  QMessageBox.Ok)
                return None
        return points
            
            
    def checkpoints(self):
        pts = self.getpoints()
        nsecs = len(pts)
        npts = sum([len(p[1]) for p in pts])
        QMessageBox.information(self, 'Pontos definidos', "Foram definindos {} pontos em {} seções distintas".format(npts, nsecs),  QMessageBox.Ok)
        self.is_read = True
        
        self.plotwin.draw_points(pts, self.eixocb.currentText())
        
        pass
    def sair(self):
        self.close()
        
        
    

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
        npts = [len(p[1]) for p in pts]
        nptstot = sum(npts)
        self.axes.set_title("Eixo {}. Total de pontos: {}".format(ax, nptstot))
        
        for i in range(nn):
            if npts[i] < 1:
                continue
            isec = pts[i][0]
            pp = np.array(pts[i][1])
            if ax=='z':
                y = pp
                x = 10.0 * (pp/500)**0.3
                
            else: # ax=='x' ou 'y':
                x = pp
                y = np.ones(len(pp))
            self.axes.plot(x, y, color=self.colors[i], marker='o', linestyle='' ,
                           label='Seção {} - {} pontos'.format(isec+1, npts[i]))

        self.axes.legend()
            
        self.draw()
        return None
    
        
if __name__ == '__main__':
    app = QApplication([])

    win = Pos1dWindow()

    win.show()

    #sys.exit(app.exec_())
    app.exec_()

    print(win.getpoints())
    
