from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QGridLayout, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, qApp, QMenu,
                             QGroupBox, QPushButton, QApplication, QSlider, QMainWindow, QSplashScreen,
                             QAction, QComboBox, QMessageBox)

from PyQt5.QtCore import Qt, QRegExp, QEventLoop, QTimer

from PyQt5.QtGui import QPixmap, QIcon, QRegExpValidator, QDoubleValidator, QIntValidator

import scanivalve


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

        self.draw_gui(ip)

        return
    
    def draw_gui(self, ip='191.30.80.131'):
        self.ipg = self.draw_connect(ip)
        self.confg = self.draw_config()
        self.opg = self.draw_operate()

        hb0 = QHBoxLayout()

        grp = QGroupBox("Scanivalve")
        
        hb = QHBoxLayout()
        #vb1 = QVBoxLayout()
        hb.addWidget(self.ipg)
        hb.addWidget(self.confg)
        hb.addWidget(self.opg)
        
        grp.setLayout(hb)
        hb0.addWidget(grp)
        self.setLayout(hb0)

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
            return False
        
        try:
            ip = self.ipt.text()
            self.scani = scanivalve(ip)
            self.connected = True
            self.ipb.setText("Desconectar")
            self.ipb.setToolTip('Desconectar o scanivalve')
            self.confg.setEnabled(True)
            self.model = self.scani.get_model()
            self.modell.setText(self.model)
            
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
    

        
    def config(self):
        if not self.connected:
            return False
        
        fps = int(self.fps['w'].text())
        avg = int(self.avg['w'].text())
        period = int(self.period['w'].text())

        self.scani.config(fps, period, avg)

        dt = self.scani.dt
        freq = 1.0 / dt
        ttot = fps * dt

        self.freql.setText('Amostragem: {:.2f} (Hz)'.format(freq))
        self.ttotl.setText('Tempo de aquisição: {:.2f} (s)'.format(ttot))

        
        
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
        
        vb.addWidget(op_lists)
        vb.addWidget(op_zero)
        vb.addWidget(op_aq)

        opg.setLayout(vb)

        return opg

    def lists(self):
        pass

    def zero(self):
        pass

    def acquire(self):
        pass
    
        
        
        
        
        
if __name__ == '__main__':
    app = QApplication([])

    win = ScaniGUI()#'192.168.0.101')

    win.show()

    #sys.exit(app.exec_())
    app.exec_()
