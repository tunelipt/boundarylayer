

import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QPixmap, QIcon, QRegExpValidator, QDoubleValidator, QIntValidator
import time

import positions as pos
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

secsdefault = ['10~580~35~1.05']

        
class Pos1dDialog(QDialog): 
    """
    Interface para especificação de movimento 1D
    """

    def __init__(self, axis='z', secs=secsdefault, nsectot=5, roundpts=1, parent=None):

        super(Pos1dDialog, self).__init__(parent)
        self.setWindowTitle('Posições de medição')
            
        if secs is None:
            secs = ['' for i in range(nsectot)]
        elif isinstance(secs, (list, tuple)):
            nsectot = max(nsectot, len(secs))
            for i in range(len(secs), nsectot):
                secs.append('')
        else:
            secs = [secs]
            for i in range(1, nsectot):
                secs.append('')

        if roundpts:
            if isinstance(roundpts, int):
                self.ndigits = roundpts
            else:
                self.ndigits = 0
            self.roundpts = True
        else:
            self.roundpts = False
            

        self.roundpts = roundpts
        self.secs = secs
        self.nsectot = nsectot

        vb0 = QVBoxLayout()
        hb = QHBoxLayout()
        vb = QVBoxLayout()
        
        self.posgb = self.poswin(axis, secs, nsectot)
        
        vb.addWidget(self.posgb)
        hb.addLayout(vb)

        dpi = 100
        width=5
        height=4
        plt = QGroupBox("Visualização dos pontos", width=width*100, height=height*dpi)
        
        vb1 = QVBoxLayout()
        
        self.plotwin = CheckPointsWindow(self, width, height, dpi)
        vb1.addWidget(self.plotwin)
        plt.setLayout(vb1)
        hb.addWidget(plt)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        vb0.addLayout(hb)
        vb0.addWidget(self.buttonBox)

        self.setLayout(vb0)
        
    
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
        axis = axis.lower()
        if axis == 'x':
            idx = 0
        elif axis=='y':
            idx = 1
        else:
            idx = 2
        self.eixocb.setCurrentIndex(idx)
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


        self.posplotbut = QPushButton("Ver os pontos")
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
                if self.roundpts:
                    p = [round(x, self.ndigits) for x in p]
                points.append((i, p, s))
            except:
                QMessageBox.critical(self, 'Erro interpretando os pontos', "Não foi possível entender o que {} quer dizer".format(s),  QMessageBox.Ok)
                return None
        axis = ['x', 'y', 'z'][self.eixocb.currentIndex()]
        return axis, points
    
            
            
    def checkpoints(self):
        axis, pts = self.getpoints()
        nsecs = len(pts)
        npts = sum([len(p[1]) for p in pts])
        QMessageBox.information(self, 'Pontos definidos', "Foram definindos {} pontos em {} seções distintas".format(npts, nsecs),  QMessageBox.Ok)
        self.is_read = True
        
        self.plotwin.draw_points(pts, self.eixocb.currentText())
        
        
        
    

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
        self.axes.set_xlabel('Velocidade')
        self.axes.set_ylabel('Altura {} (mm)'.format(ax))

        npts = [len(p[1]) for p in pts]
        nptstot = sum(npts)
        self.axes.set_title("Eixo {}. Total de pontos: {}".format(ax, nptstot))
        
        for i in range(nn):
            if npts[i] < 1:
                continue
            isec = pts[i][0]
            pp = np.array(pts[i][1])
            if ax=='z':
                x = 10.0 * (pp/500)**0.3
                y = pp
            else: # ax=='x' ou 'y':
                x = pp
                y = 10*np.ones(len(pp))
            self.axes.plot(x, y, color=self.colors[i], marker='o', linestyle='' ,
                           label='Seção {} - {} pontos'.format(isec+1, npts[i]))

        self.axes.legend()
            
        self.draw()
        return None
    
        
if __name__ == '__main__':
    app = QApplication([])

    win = Pos1dDialog('x', ['50:200:40'])#, '300:2400:100', '2440:2600:40'])
    ret = win.exec_()
    print(ret)
    if ret:
        axis, pts = win.getpoints()
        print('Eixo: {}'.format(axis))
        print(pts)
    else:
        print("NADA")
        
    
