from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox, QCheckBox)

from PyQt5.QtCore import Qt, QRegExp, QEventLoop, QTimer
from PyQt5 import QtCore

from PyQt5.QtGui import QPixmap, QIcon, QRegExpValidator, QDoubleValidator, QIntValidator
import time




import numpy as np
import scanivalve

class Pitot(object):

    def __init__(self, cd=0.997, rho=1.08):

        self.cd = cd
        self.rho = 1.08

    def __call__(self, dp, rho=None):

        if rho is None:
            rho = self.rho

        return self.cd * np.sqrt(2*dp/rho)


class ChannelConfig(object):

    def __init__(self, chans):

        
        self.nch = len(chans)
        
        self.chans = [ch for ch in chans]
        self.selected = [False for i in range(self.nch)]

    def available(self, chidx):
        return not self.selected[chidx]
    
    def check(self, chidx):
        self.selected[chidx] = True

    def uncheck(self, chidx):
        self.selected[chidx] = False

    def findfirst(self):
        for i in range(self.nch):
            if not self.selected[i]:
                self.selected[i] = True
                return i
        return -1
    
    def names(self):

        return self.chans
    def nchans(self):
        return self.nch
    

class PitotConfig(QWidget):

    def __init__(self, lab, chans, Cd=0.997, chtot=15, chest=16, parent=None):
        super(PitotConfig, self).__init__(parent)
        self.lab = lab
        self.Cd = Cd
        self.chans = chans

        self.itot = chtot
        self.iest = chest
        self.draw_gui()


    def draw_gui(self):

        self.grp = QGroupBox(self.lab)

        vb = QVBoxLayout()
        hb1 = QHBoxLayout()
        hb2 = QHBoxLayout()
        hb3 = QHBoxLayout()

        self.ittext = None
        self.ietext = None
        

        cdlab = QLabel("Cd")
        self.cdtext = QLineEdit(str(self.Cd))
        cdval = QDoubleValidator(0.0001, 9.9999, 4)
        self.cdtext.setValidator(cdval)
        hb1.addWidget(cdlab)
        hb1.addWidget(self.cdtext)
        self.cdtext.setToolTip("Valor do coeficiente de descarga do tubo de Pitot")

        itlab = QLabel("Canal da pressão total")
        self.ittext = QComboBox()
        for ii in self.chans.names():
            self.ittext.addItem(ii)
        self.ittext.setToolTip("Canal da tomada de pressão total do tubo de Pitot")
        self.ittext.setCurrentIndex(self.itot)
        
        hb2.addWidget(itlab)
        hb2.addWidget(self.ittext)

        ielab = QLabel("Canal da pressão estática")
        self.ietext = QComboBox()
        for ii in self.chans.names():
            self.ietext.addItem(ii)
        self.ietext.setToolTip("Canal da tomada de pressão estática do tubo de Pitot")
        self.ietext.setCurrentIndex(self.iest)

        self.chans.check(self.itot)
        self.chans.check(self.iest)
        
        self.ietext.currentIndexChanged.connect(self.selectionchange)
        self.ittext.currentIndexChanged.connect(self.selectionchange)
        

        hb3.addWidget(ielab)
        hb3.addWidget(self.ietext)

        vb.addLayout(hb1)
        vb.addLayout(hb2)
        vb.addLayout(hb3)

        self.chbx = QCheckBox("Usar este Pitot?")
        self.chbx.stateChanged.connect(self.clickcheck)
        self.chbx.setChecked(True)

        self.grp.setLayout(vb)
        vb0 = QVBoxLayout()

        
        vb0.addWidget(self.grp)
        vb0.addWidget(self.chbx)
        
        self.setLayout(vb0)
        return

    def clickcheck(self, state):

        chk = self.chbx.isChecked()

        if chk:
            self.grp.setEnabled(True)
        else:
            self.grp.setEnabled(False)

    def checked(self):

        return self.chbx.isChecked()
    
    def selectionchange(self):
        i1 = self.ittext.currentIndex()
        i2 = self.ietext.currentIndex()
        if i1 == i2:
            QMessageBox.critical(self, 'Canais iguais',
                                 "Não faz sentido canais iguais em um tubo de Pitot!",
                                 QMessageBox.Ok)
            return

        if i1 != self.itot:
            self.chans.uncheck(self.itot)
            self.itot = i1
            if not self.chans.available(i1):
                QMessageBox.warning(self, 'Canal já usado',
                                    "Faz sentido? Usando o canal {} como pressão total".format(self.chans.names()[i1]), QMessageBox.Ok)
            self.chans.check(i1)
            
                
        if i2 != self.iest:
            self.chans.uncheck(self.iest)
            self.iest = i2
            if not self.chans.available(i2):
                QMessageBox.warning(self, 'Canal já usado',
                                    "Faz sentido? Usando o canal {} como pressão estática".format(self.chans.names()[i2]), QMessageBox.Ok)
            self.chans.check(i2)


        print(self.chans.selected)
        return
    def pitot(self):
        Cd = self.getcd()
        itot = self.getitot()
        iest = self.getiest()
        chk = self.checked()
        
        return chk, Cd, itot, iest
    
        
    def getcd(self):
        return float(self.cdtext.text())
    def getitot(self):
        return int(self.ittext.currentIndex())
    def getiest(self):
        return int(self.ietext.currentIndex())
        
        

        
class ChannelConnect(QWidget):

    def __init__(self, s, chans, idx, chk=True, parent=None):

        super(ChannelConnect, self).__init__(parent)

        self.chans = chans

        hb = QHBoxLayout()

        self.chbx = QCheckBox(s)
        self.chbx.setChecked(chk)
        
        self.lst = QComboBox()
        for ii in self.chans.names():
            self.lst.addItem(ii)
        self.lst.setCurrentIndex(idx)
        hb.addWidget(self.chbx)
        hb.addWidget(self.lst)


        self.idx = idx
        self.lst.currentIndexChanged.connect(self.selectionchange)
        self.chbx.stateChanged.connect(self.clickcheck)
        self.lst.setEnabled(chk)
        self.setLayout(hb)

    def selectionchange(self):
        i = self.lst.currentIndex()

        if i != self.idx:
            self.chans.uncheck(self.idx)
            self.idx = i
            if not self.chans.available(i):
                QMessageBox.warning(self, 'Canal já usado',
                                    "Faz sentido? Usando o canal {} como pressão total".format(self.chans.names()[i]), QMessageBox.Ok)
            self.chans.check(i)

        return
    def clickcheck(self, state):

        chk = self.chbx.isChecked()
        
        if chk:
            self.lst.setEnabled(True)
        else:
            self.lst.setEnabled(False)

    def checked(self):
        return self.chbx.isChecked()
    def index(self):
        return self.lst.currentIndex()
    
class PitotWin(QMainWindow):


    def __init__(self, chans, parent=None):
        

        super(PitotWin, self).__init__(parent)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.scani = None
        hb = QHBoxLayout()
        vb = QVBoxLayout()

        self.pitotw = PitotConfig("Pitot", chans, 0.997, 15, 16)
        self.pitotwref = PitotConfig("Pitot de Ref.", chans, 0.997, 13, 14)
        hb.addWidget(self.pitotw)
        hb.addWidget(self.pitotwref)
        
        vb.addLayout(hb)

        hb2 = QHBoxLayout()

        grp = QGroupBox("Outras medidas")
        vb2 = QVBoxLayout()
        self.anel_mesa = ChannelConnect("Anel da Mesa", chans, 10)
        self.anel_mesa.setToolTip("Anel piezométrico na mesa do túnel")
        
        self.anel_porta = ChannelConnect("Anel da Porta", chans, 11)
        self.anel_porta.setToolTip("Anel piezométrico na porta do túnel")

        #self.anel_contracin = ChannelConnect("Entrada da contração", chans, 9, False)
        #self.anel_porta.setToolTip("Anel piezométrico na porta do túnel")

        #self.anel_contracout = ChannelConnect("Saída da  contração", chans, 8, False)
        self.patm = ChannelConnect("Pressão atmosférica", chans, 1, True)
        self.patm.setToolTip("Tomada de pressão aberta para a atmosfera")
                
        vb2.addWidget(self.anel_mesa)
        vb2.addWidget(self.anel_porta)
        #vb2.addWidget(self.anel_contracin)
        #vb2.addWidget(self.anel_contracout)
        vb2.addWidget(self.patm)

        grp.setLayout(vb2)

        hb2.addWidget(grp)

        grp2 = QGroupBox()
        hb3 = QHBoxLayout()
        hb3.addWidget(QLabel("Massa específica(kg/m³)"))
        self.rhotext = QLineEdit("1.08")
        val = QDoubleValidator(0.7, 1.5, 2)
        self.rhotext.setValidator(val)
        hb3.addWidget(self.rhotext)
        grp2.setLayout(hb3)
        
        hb2.addWidget(grp2)
                
        vb.addLayout(hb2)
        self.widget.setLayout(vb)
        
        self.setWindowTitle('Configuração dos Pitots')

    def pitot(self):
        return self.pitotw.pitot()
    
    def pitotref(self):
        return self.pitotwref.pitot()

    def config(self):
        pitot = self.pitotw.pitot()
        pitotref = self.pitotwref.pitot()
        amesa = (self.anel_mesa.checked(), self.anel_mesa.index())
        aporta = (self.anel_porta.checked(), self.anel_porta.index())
        patm = (self.patm.checked(), self.patm.index())
        rho = float(self.rhotext.text())

        return dict(pitot=pitot, pitotref=pitotref, mesa=amesa, porta=aporta, patm=patm, rho=rho)
    

if __name__ == '__main__':
    app = QApplication([])

    chans = ["Canal {}".format(i) for i in range(17)]
    chans[0] = "REF"
    
    win = PitotWin(ChannelConfig(chans))

    win.show()

    #sys.exit(app.exec_())
    app.exec_()

    print(win.config())
    
        
