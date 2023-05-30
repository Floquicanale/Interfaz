import serial, time
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp


class Pan_Tom_QRS():

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
      y(nT) = 32x(nT - 16T) - y(nT - T) - x(nT) + x(nT - 32T)
    '''
        # Initialize result
        result = None

        # Create a copy of the input signal
        y = x.copy()
        
        # Apply the low pass filter using the equation given
        for index in range(len(x)):
            y[index] = x[index]

            if (index >= 1):
                y[index] += 2*y[index-1]

            if (index >= 2):
                y[index] -= y[index-2]

            if (index >= 6):
                y[index] -= 2*x[index-6]

            if (index >= 12):
                y[index] += x[index-12] 
            
        # Copy the result of the low pass filter
        result = y.copy()
        # Apply the high pass filter using the equation given
        for index in range(len(x)):
            result[index] = -1*y[index]

            if (index >= 1):
                result[index] -= result[index-1]

            if (index >= 16):
                result[index] += 32*y[index-16]

            if (index >= 32):
                result[index] += y[index-32]

        # Normalize the result from the high pass filter
        max_val = max(max(result),-min(result))
        result = result/max_val

        return result
    


'''
Codigo principal
Se usa un ciclo while para tomar datos de la señal a la cual se le aplica recursivamente Pan_Tom_QRS.
Primero hay que tomar un segmento de la señal y hacerle el procedimiento, este mismo cachito se guarda para recursividad
'''
# Inicializar variables
ard = serial.Serial('COM5',9600)
fs = 9600  

ecg_buffer = np.zeros(2000)  # Búfer para almacenar los últimos 2000 puntos de ECG
filtrada = np.zeros(2000)
picos = []

long_ventana = 10
start_time = time.time()
TiempoFinal = 50 # Define el tiempo total de adquisición
run = True

QRS_detector = Pan_Tom_QRS()

try:
    while run:
        # Leer una línea completa de datos hasta encontrar \n
        linea = ard.readline().decode().strip()
        print(linea)
        data = float(linea)

        ecg_buffer = np.append(ecg_buffer, data)
        l = len(ecg_buffer)

        if(l>4000):
            ecg_buffer = ecg_buffer[1999:] #elimino la ultima ventana
            filtrada = QRS_detector.pasabanda(ecg_buffer)

except KeyboardInterrupt:
    # Manejar la interrupción del teclado para detener la adquisición de datos
    ard.close()

