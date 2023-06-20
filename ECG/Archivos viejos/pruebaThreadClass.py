from PyQt5.QtCore import Qt, QThread, QTimer, QRunnable
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QFont, QColor
import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
import sys
import serial
from scipy.signal import butter, filtfilt
import scipy as sp
import numpy as np
import logging

class SerialReadThread(QThread):
    data_received = QtCore.pyqtSignal(float)

    def __init__(self, serial_port):
        super(SerialReadThread, self).__init__()
        self.serial_port = serial_port
        self.stopThread = False

    def run(self):
        while not self.stopThread:
            line = self.serial_port.readline().decode('utf-8').strip()
            try:
                value = float(line)
                self.data_received.emit(value)
                PanTompkinsThread(value).start()
                #time.sleep(1)
            except ValueError:
                pass

    def stop(self):
        self.stopThread = True

class PanTompkinsThread(QRunnable):
    fs = 250
    ecg_buffer = np.zeros(int(fs*0.2))  # Buffer para almacenar los puntos de ECG

    def __init__(self, valor):
        super(PanTompkinsThread, self).__init__()
        self.valor = valor
        self.stopThread = False

    def run(self):
        self.PanTom()

    def PanTom(self):
        valor = self.valor
        l = len(self.ecg_buffer)

        if(l<1750):
            self.ecg_buffer = np.append(self.ecg_buffer, valor)

        #Cuando se actualiza el buffer se agregan 2 segundos de data
        elif(l>=1750):
            output = self.resolver(self.ecg_buffer, self.fs)

            #umbral adaptativo
            umbral = 0.7*max(output)
        
            # Busco los picos
            picos = sp.signal.find_peaks(output, height=umbral, distance=self.fs*0.67)

            #Frecuencia cardiaca y esas cosas
            frecuencia = self.frequency(picos, self.fs)
            Ui_MainWindow.LCD.display(round(frecuencia,0))
            #ACA HAY QUE CAMBIAR LO QUE MUESTRA EL DISPLAY
            #Cardiac_Freq.annotation() #anota en el csv que hubo un pico 

            self.ecg_buffer = self.ecg_buffer[500:] #elimino los primeros pip valores

        
        return

    def pasabanda(self, x):
        '''
    Filtro PasaBnada
    :param signal: señal de entrada 
    :return: señal procesada

    Metodología:
    Usamos un filtro pasabanda para atenuar el ruido. 
    Necesitamos solo las señales con frecuencia de 5 a 15 Hz, 
    para quedarnos con estas primero usamos un pasabajos y luego un pasaaltos en cadena.

    Ecuacion recursiva del pasabajos:
      y(nT) = 2y(nT - T) - y(nT - 2T) + x(nT) - 2x(nT - 6T) + x(nT - 12T)

    Ecuacion recursiva del pasaaltos:
      y(nT) = 32x(nT - 16T) - [y(nT - T) + x(nT) - x(nT - 32T)]
    
      fuente: https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf
      El corte inferior es de 5Hz el superior en 11 Hz la ganancia de 32 para el pasaaltos y 36 pasabajos.
    '''
        # El resultado empieza siendo nada
        result = None

        # La copia de la señal va a ser y
        y = x.copy()
        
        # Aplicamoes el pasabajos de segundo orden 
        for index in range(len(x)):
            y[index] = x[index] #vendria a ser la parte del x(nT)

            if (index >= 1):
                y[index] += 2*y[index-1] #primer termino

            if (index >= 2):
                y[index] -= y[index-2] #segundo

            if (index >= 6):
                y[index] -= 2*x[index-6] #cuerto

            if (index >= 12):
                y[index] += x[index-12] #ultimo
            
        result = y.copy()
        # Aplicamos el filtro pasaaltos
        for index in range(len(x)):
            result[index] = -1*y[index] #vendria a ser el -x(nT)

            if (index >= 1):
                result[index] -= result[index-1]

            if (index >= 16):
                result[index] += 32*y[index-16]

            if (index >= 32):
                result[index] += y[index-32]

        # Normalizando el valor de la salida del filtro
        max_val = max(max(result),-min(result))
        result = result/max_val

        return result
    
    def derivada(self, x):
        '''
    Filtro Derivativo 
    :param signal: señal de entrada 
    :return: señal derivada

    Metodología:
    Usamos un filtro derivativo de 5 puntos para obtener la pendiente de los picos. 
    El gráfico del filtro es lineal hasta los 30 Hz lo que lo 
    aproxima a una derivada ideal.

    Ecuacion recursiva del integrador:
      y(nT) = (1/8T)[-x(nT - 2T) - 2x(nT - T) + 2x(nT + T) + x(nT + 2T)]
    
      fuente: https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf
      '''
        
        #Mismo procedimiento que para los otros filtros

        result = x.copy()

        #Aplicamos el filtro
        for index in range(len(x)):
            result[index] = 0 #empieza siendo cero en todas partes

            if (index >= 1):
                result[index] -= 2*x[index-1]
            
            if (index >= 2):
                result[index] -= x[index-2]
            
            if (index >=2 and index <= len(x)-3):
                result[index] += x[index+2]

            if (index >=2 and index <= len(x)-2):
                result[index] += 2*x[index + 1]

            result[index] = result[index]/8

        return result
    
    def cuadrado(self, x):
        '''
    Elevar al cuadrado 
    :param signal: señal de entrada 
    :return: señal elevada al cuadrado

    Metodología:
    Se eleva al cuadrado la señal para quedarnos con todos valores positivos

    Ecuacion:
      y(nT) = [x(nT)]^2
    
      fuente: https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf
      '''
        
        result = x.copy()

        for index in range(len(x)):
            result[index] = x[index]**2
        
        return result
    
    def integrador(self, x, fs):
        '''
    Integrador de ventana móvil
    :param signal: señal de entrada 
    :return: señal integrada

    Metodología:
    La idea es ver la duración de la onda. Por lo general el largo de la ventena debería ser
    aproximadamente el máximo valor del largo de un QRS. 
    Hay que buscarlo empíricamente, para el paper usado como bibliografía usan Fs = 200 Hz
    y la ventana de 30 muestras (150 ms). 

    Ecuacion de integrador con ventana móvil:
      y(nT) = 1/N [x(nT - (N-1)T) + x(nT - (N-2)T) + ... + x(nT)]
    
      fuente: https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf
      '''
        largo_ventana = 0.150 #esta en segundos chequear empiricamente
        result = x.copy()
        ventana = round(largo_ventana*fs)
        suma = 0

        #calculo de la suma para los primeros N terminos, todavia no alcanza para restar nada
        for i in range(ventana):
            suma += x[i]/ventana
            result[i] = suma

        for index in range(ventana, len(x)):
            suma += x[index]/ventana
            suma -= x[index-ventana]/ventana
            result[index] = suma

        return result

    def resolver(self, x, fs):

        # Bandpass Filter
        global bpass
        bpass = self.pasabanda(x.copy())

        # Derivative Function
        global der
        der = self.derivada(bpass.copy())

        # Squaring Function
        global sqr
        sqr = self.cuadrado(der.copy())

        # Moving Window Integration Function
        global mwin
        mwin = self.integrador(sqr.copy(), fs)

        return mwin

    def frequency(self, peaks, fs):
        distance = 0
        prom = 0
        frec=0
        if len(peaks[0])==0:
            pass
        else:
            for i in range(len(peaks[0])):
                if(i+1<len(peaks[0])):
                    distance = peaks[0][i+1]-peaks[0][i]
                    prom += distance
            if(len(peaks[0])>1):
                prom = prom/(len(peaks[0])-1)
                frec = 60/(prom/fs)
        
        return frec

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
        self.graphWidget.setYRange(0,1100)
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
        #self.start_register.clicked.connect(self.PanTom)
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
                self.serial_port = serial.Serial('COM3', 9600)                
                self.serial_read_thread = SerialReadThread(self.serial_port)            
                self.serial_read_thread.data_received.connect(self.update_graph)
                self.serial_read_thread.start()
            except serial.SerialException:
                logging.debug("No se pudo abrir el puerto COM3")
        else:
            self.start_register.setText("Iniciar registro")
            if self.serial_port is not None:
                self.serial_read_thread.stop()
                self.serial_port.close()
                self.serial_port = None

    def rec(self):

        if self.record.isChecked(): 
            self.record.setText("Detener grabación")
        else:
            self.record.setText("Iniciar grabación")
        return 
    
    def update_graph(self, new_data):
        # Agregar nuevos datos al conjunto de datos
        self.data.extend([new_data])

        #Pasabandas
        #filtered_data = self.bp(self.data)

        # Limitar el conjunto de datos a `max_samples` muestras
        if len(self.data) > self.max_samples:
            self.data = self.data[-self.max_samples:]

        # Actualizar el gráfico
        self.curve.setData(self.data)

    def bp(self, data):
        # Frecuencias de corte
        fs = 250 
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
