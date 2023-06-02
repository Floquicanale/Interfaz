from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QFont, QColor
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
import sys
import serial
from scipy.signal import butter, filtfilt
import numpy as np
from brainflow.data_filter import DataFilter

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        #Tamaño de MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 442)
        screen_geometry = QtWidgets.QDesktopWidget().availableGeometry()
        
        #Seteo Central Widget
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setTitle("Elecrocardiograma")
        self.graphWidget.setXRange(0,1000)
        self.graphWidget.setYRange(-1000,1000)
        MainWindow.setCentralWidget(self.graphWidget)

        #Boton de iniciar/parar registro (toggle)
        self.start_register = QtWidgets.QPushButton(self.graphWidget)
        self.start_register.setGeometry(QtCore.QRect(screen_geometry.width()-190, 130, 150, 50))
        self.start_register.setObjectName("start_register")
        self.start_register.setCheckable(True)

        #Boton de iniciar/parar grabación de datos (toggle)
        self.record = QtWidgets.QPushButton(self.graphWidget)
        self.record.setGeometry(QtCore.QRect(screen_geometry.width()-190, 200, 150, 50))
        self.record.setObjectName("record")
        self.record.setCheckable(True)

        #Display frecuencia cardíaca
        self.label = QtWidgets.QLineEdit(self.graphWidget)
        self.label.setGeometry(QtCore.QRect(screen_geometry.width()-350, 550, 300, 50))
        self.label.setObjectName("label")   
        self.LCD = QtWidgets.QLCDNumber(self.graphWidget)
        self.LCD.setGeometry(QtCore.QRect(screen_geometry.width()-350, 600, 300, 100))
        self.LCD.setObjectName("LCD")      

        #Retranslate
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        #Connect
        self.start_register.clicked.connect(self.start)
        self.start_register.clicked.connect(self.PanTom)
        self.record.clicked.connect(self.rec)

        #Variables para el gráfico
        self.max_samples = 1000 #Me quedo con 1000 muestras
        self.data = []
        self.curve = self.graphWidget.plot()
        self.curve = self.graphWidget.plot(pen=pg.mkPen(color='r', width=2))

        #Conexión con Arduino
        self.serial_port = None

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        #Seteo iniciar/parar registro
        self.start_register.setText(_translate("MainWindow", "Iniciar registro"))
        font = QFont("Arial", 12, QFont.Bold)
        self.start_register.setFont(font)

        #Seteo iniciar/parar grabación de datos
        self.record.setText(_translate("MainWindow", "Grabar registro"))
        self.record.setStyleSheet("QPushButton {background-color:red}")
        self.record.setFont(font)

        #Seteo label frec cardiaca
        font = QFont("Arial", 14, QFont.Bold)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setText(_translate("MainWindow", "FRECUENCIA CARDÍACA"))
        self.label.setStyleSheet("QLabel {background-color: black; color: white;}")
    
    def start(self):

        if self.start_register.isChecked(): 
            self.start_register.setText("Detener registro")
            try:
                self.serial_port = serial.Serial('COM3', 9600)  # Ajustá el puerto y la velocidad de acuerdo a tu configuración
                self.read_serial_data()  # Iniciar la lectura de datos
            except serial.SerialException:
                print("No se pudo abrir el puerto COM3")
        else:
            self.start_register.setText("Iniciar registro")
            if self.serial_port is not None:
                self.serial_port.close()
                self.serial_port = None
        return

    def rec(self):

        if self.record.isChecked(): 
            self.record.setText("Detener grabación")
        else:
            self.record.setText("Iniciar grabación")
        return 

    def PanTom(self):
        #Esta funcion, o alguna auxiliar, actualiza el valor del LCD de frec cardiaca.
        #Lo clave en 60 para probar
        self.LCD.display(60)
        return
    
    def read_serial_data(self):
        line = self.serial_port.readline().decode('utf-8').strip()
        # Convertir los datos a números 
        try:
            value = float(line)
            self.update_graph([value])
        except ValueError:
            pass

        if self.start_register.isChecked():
            QtCore.QTimer.singleShot(0, self.read_serial_data)  # Leer los datos en el siguiente ciclo
    
    def update_graph(self, new_data):
        # Agregar nuevos datos al conjunto de datos
        self.data.extend(new_data)

        #Pasabandas
        filtered_data = self.bp(self.data)

        # Limitar el conjunto de datos a `max_samples` muestras
        if len(self.data) > self.max_samples:
            self.data = self.data[-self.max_samples:]

        # Actualizar el gráfico
        self.curve.setData(self.data)

    def bp(self, data):
        # Frecuencias de corte
        fs = 150 
        lowcut = 0.5
        highcut = 50

        # Diseñar los coeficientes del filtro
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(2, [low, high], btype='band')

        # Aplicar el filtro a los datos
        filtered_data = filtfilt(b, a, data)

        return filtered_data

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Electrocardiograma")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape or event.key() == QtCore.Qt.Key_Space:
            self.showNormal()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
      
    window.showFullScreen()
    app.installEventFilter(window)
    sys.exit(app.exec_())
