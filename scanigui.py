from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox, QProgressBar)

from PyQt5.QtCore import Qt, QRegExp, QEventLoop, QTimer

from PyQt5.QtGui import QPixmap, QIcon, QRegExpValidator, QDoubleValidator, QIntValidator

import scanivalve
import time

def mysleep(ns):
    loop = QEventLoop()
    QTimer.singleShot(ns*1000, loop.quit)
    loop.exec_()
    return None


class ScaniGUI(QWidget):

    def __init__(self, ip='191.30.80.131', parent=None):
        
        super(ScaniGUI, self).__init__(parent)

        self.scani = None
        self.connected = False
        self.fps = dict(val=1, w=None, validator=QIntValidator(1, 10000000),
                        tip="Número de amostras a serem lidas", 
                        xmin=1, xmax=10000000)
        self.avg = dict(val=16, w=None, validator=QIntValidator(1,240),
                        tip = "Número de médias de amostras",
                        xmin=1, xmax=240)
        self.period = dict(val=500, w=None, validator=QIntValidator(150, 62000),
                           tip = "Tempo de leitura em cada sensor em μs",
                           xmin=150, xmax=65000)
        self.ip = ''
        self.draw_gui(ip)
        self.confg.setEnabled(False)
        self.opg.setEnabled(False)

        return
    
    def draw_gui(self, ip='191.30.80.131'):
        self.ipg = self.draw_connect(ip)
        self.confg = self.draw_config()
        self.opg = self.draw_operate()
        
        vb0 = QVBoxLayout()

        grp = QGroupBox("Scanivalve")
        
        hb = QHBoxLayout()
        #vb1 = QVBoxLayout()
        hb.addWidget(self.ipg)
        hb.addWidget(self.confg)
        hb.addWidget(self.opg)
        
        grp.setLayout(hb)
        vb0.addWidget(grp)
        self.progress = QProgressBar()
        vb0.addWidget(self.progress)
        self.progress.setVisible(False)
        self.setLayout(vb0)
        
    def draw_connect(self, ip='191.30.80.131'):

        ipg = QGroupBox("Conexão")
        vb1 = QVBoxLayout()
        hb1 = QHBoxLayout()
        hb1.addWidget(QLabel("IP"))
        self.ipt = QLineEdit(ip)
        self.ipt.setToolTip('Endereço IP do scanivalve')
        hb1.addWidget(self.ipt)
        vb1.addLayout(hb1)
        self.ipb = QPushButton("Conectar")
        self.ipb.setToolTip('Conectar o scanivalve')
        
        vb1.addWidget(self.ipb)
        self.ipb.clicked.connect(self.connect)

        self.modell = QLabel("")
        vb1.addWidget(self.modell)
        
        ipg.setLayout(vb1)
        return ipg
        

    def connect(self):
        if self.connected:
            self.scani.close()
            self.ipb.setText("Conectar")
            self.ipb.setToolTip('Conectar o scanivalve')
            self.connected = False
            self.scani = None
            self.ip = ''
            self.confg.setEnabled(False)
            self.opg.setEnabled(False)
            return False
        
        try:
            ip = self.ipt.text()
            self.ip = ip
            self.scani = scanivalve.Scanivalve(ip)
            self.connected = True
            self.ipb.setText("Desconectar")
            self.ipb.setToolTip('Desconectar o scanivalve')
            self.confg.setEnabled(True)
            self.model = self.scani.get_model()

            self.config_model(self.model)
            
            self.modell.setText('Modelo DSA-{}'.format(self.model))
            self.confg.setEnabled(True)
            self.opg.setEnabled(True)
            self.fps['w'].setText(str(self.scani.FPS))
            self.avg['w'].setText(str(self.scani.AVG))
            self.period['w'].setText(str(self.scani.PERIOD))
            self.display_config()
            
            return True
        except:
            QMessageBox.critical(self, 'Erro conectando ao Scanivalve',
                                 "Verifique a rede ou o scanivalve para encontrar problemas",
                                 QMessageBox.Ok)
            self.scani = None
            self.connected = False
            return False

    def config_model(self, model):
        if model == '3017':
            self.period['xmin'] = 500
            self.period['validator'].setBottom(500)
            self.avg['xmax'] = 32767
            self.avg['validator'].setTop(32767)
        else:
            self.period['xmin'] = 150
            self.period['validator'].setBottom(150)
            self.avg['xmax'] = 240
            self.avg['validator'].setTop(240)
        
    def draw_config(self):

        confg = QGroupBox("Configuração")
        vb = QVBoxLayout()
        hb1 = QHBoxLayout()
        hb2 = QHBoxLayout()
        hb3 = QHBoxLayout()

        
        hb1.addWidget(QLabel("FPS"))
        self.fps['w'] = QLineEdit(str(self.fps['val']))
        self.fps['w'].setValidator(self.fps['validator'])
        self.fps['w'].setToolTip(self.fps['tip'])
        hb1.addWidget(self.fps['w'])
        
        hb2.addWidget(QLabel("AVG"))
        self.avg['w'] = QLineEdit(str(self.avg['val']))
        self.avg['w'].setValidator(self.avg['validator'])
        self.avg['w'].setToolTip(self.avg['tip'])
        hb2.addWidget(self.avg['w'])

        hb3.addWidget(QLabel("PERIOD"))
        self.period['w'] = QLineEdit(str(self.period['val']))
        self.period['w'].setValidator(self.period['validator'])
        self.period['w'].setToolTip(self.period['tip'])
        hb3.addWidget(self.period['w'])

        self.freql = QLabel("")
        self.ttotl = QLabel('')
        self.confb = QPushButton('Configurar')
        self.confb.setToolTip("Configurar a aquisição do scanivalve")
        self.confb.clicked.connect(self.config)
        
        vb.addLayout(hb1)
        vb.addLayout(hb2)
        vb.addLayout(hb3)
        vb.addWidget(self.freql)
        vb.addWidget(self.ttotl)
        vb.addWidget(self.confb)

        confg.setLayout(vb)

        return confg
    

    def display_config(self):
        dt = self.scani.dt
        fps = self.scani.FPS
        freq = 1.0 / dt
        ttot = fps * dt
        
        self.freql.setText('Amostragem: {:.2f} (Hz)'.format(freq))
        self.ttotl.setText('Tempo de aquisição: {:.2f} (s)'.format(ttot))
        
    def config(self):
        if not self.connected:
            return False
        if self.scani.acquiring:
            QMessageBox.critical(self, 'Erro',
                                 'Scanivalve está adquirindo dados. Espere o final ou pare a aquisição',
                                 QMessageBox.Ok)
            return False
            
        try:
            fps = int(self.fps['w'].text())
            avg = int(self.avg['w'].text())
            period = int(self.period['w'].text())

            self.scani.config(fps, period, avg)
            self.display_config()
            return True
        except:
            QMessageBox.critical(self, 'Erro',
                                 'Erro ao configurar o scanivalve',
                                 QMessageBox.Ok)
            return False
        
        
    def draw_operate(self):

        opg = QGroupBox("Operação")
        vb = QVBoxLayout()

        op_lists = QPushButton("LIST S")
        op_lists.setToolTip("Listar parâmetros de aquisição")
        op_lists.clicked.connect(self.lists)

        op_zero = QPushButton("Hard ZERO")
        op_zero.setToolTip("Zerar Scanivalve")
        op_zero.clicked.connect(self.zero)

        op_aq = QPushButton("Ler Pressão")
        op_aq.setToolTip("Adquirir pressão com configuração atual")
        op_aq.clicked.connect(self.acquire)

        op_stop = QPushButton("STOP")
        op_stop.setToolTip("Parar de fazer qualquer coisa no scanivalve")
        op_stop.clicked.connect(self.stop)
        
        vb.addWidget(op_lists)
        vb.addWidget(op_zero)
        vb.addWidget(op_aq)
        vb.addWidget(op_stop)

        opg.setLayout(vb)

        self.op_buts = dict(lists=op_lists, zero=op_zero, aq=op_aq, stop=op_stop)
        
        return opg

    def lists(self):
        if self.scani.acquiring:
            QMessageBox.critical(self, 'Erro',
                                 'Scanivalve está adquirindo dados. Espere o final ou pare a aquisição',
                                 QMessageBox.Ok)
            return False
        try:
            if self.connected:
                s = ['{} = {}\n'.format(x[1], x[2]) for x in self.scani.list_any('S')]
                print(s)
                QMessageBox.information(self, 'Configuração do scanivalve',
                                        ''.join(s), QMessageBox.Ok)
                return True
            else:
                raise RuntimeError("Não comunicou")
        except:
            QMessageBox.critical(self, 'Erro', 'Não foi possível ler a configuração do scanivalve',
                                 QMessageBox.Ok)
            return False
        return False
    

    def zero(self):
        if self.scani.acquiring:
            QMessageBox.critical(self, 'Erro',
                                 'Scanivalve está adquirindo dados. Espere o final ou pare a aquisição',
                                 QMessageBox.Ok)
            return False

        try:
            self.progress.setVisible(True)
            self.progress.setMaximum(100)
            self.progress.setValue(0)

            self.ipg.setEnabled(False)
            self.confg.setEnabled(False)

            for k,v in self.op_buts.items():
                v.setEnabled(False)
            
            self.scani.hard_zero()
            tstart = time.monotonic()
            tint = 8.0
            while True:
                mysleep(0.5)
                dt = time.monotonic() - tstart
                self.progress.setValue(dt/tint * 100)
                if dt > tint:
                    break
                
            self.ipg.setEnabled(True)
            self.confg.setEnabled(True)

            for k,v in self.op_buts.items():
                v.setEnabled(True)
            
            self.progress.setVisible(False)
        
        except:
            pass

    def acquire(self):
        if self.scani.acquiring:
            QMessageBox.critical(self, 'Erro',
                                 'Scanivalve está adquirindo dados. Espere o final ou pare a aquisição',
                                 QMessageBox.Ok)
            return False


        self.progress.setVisible(True)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        
        self.ipg.setEnabled(False)
        self.confg.setEnabled(False)
        for k,v in self.op_buts.items():
            if k != "stop":
                v.setEnabled(False)
        err = False
        
        try:
                
            ntot = self.scani.FPS

            self.scani.start()
            
            while True:
                mysleep(1)
                ns = self.scani.samplesread()
                self.progress.setValue( ns / ntot * 100)

                if ns > (ntot-2):
                    break
                if not self.scani.acquiring:
                    break

            p,f = self.scani.read()
            self.progress.setValue(100)

            pm = p.mean(0)
            pshow = ['Canal {}:     {:.1f}\n'.format(i+1, pm[i]) for i in range(16)]
            
            QMessageBox.information(self, 'Pressão média',
                                    ''.join(pshow), QMessageBox.Ok)
            

        except:
            QMessageBox.critical(self, 'Erro',
                                 'Erro na aquisição da pressão!', 
                                 QMessageBox.Ok)
            err = True
        
        self.progress.setVisible(False)
        self.ipg.setEnabled(True)
        self.confg.setEnabled(True)
        for k,v in self.op_buts.items():
            if k != "stop":
                v.setEnabled(True)
                
        
            self.stop()
            return False
        
    
    def stop(self):
        try:
            self.scani.stop()
            self.scani.clear()
            mysleep(1.0)
            return True
        except:
            QMessageBox.critical(self, 'Erro',
                                 'Não sei o que aconteceu mas o STOP não funcionou!', 
                                 QMessageBox.Ok)
            return False
        return False
    
        
        
        
        
if __name__ == '__main__':
    app = QApplication([])

    win = ScaniGUI()#'192.168.0.101')

    win.show()

    #sys.exit(app.exec_())
    app.exec_()