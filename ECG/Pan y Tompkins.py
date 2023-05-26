import serial, time
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp

ard = serial.Serial('COM5',9600)


def pam_tom(data):
    global ecg_buffer, picos
    # FILTRO PASABANDAS
    ecg_filtro = sp.signal.lfilter(b, a, linea)
    filtrado.append = ecg_filtro
    #Derivada
    derivada = np.diff(ecg_filtro)
    #Cuadrado de la señal
    squared_signal = derivada ** 2
    #Promedio movil en una ventana de 150 ms
    averaged_signal = np.convolve(squared_signal, np.ones((m,))/m, mode='valid')

    #cuales son los valores que superan el threshold y donde estan
    threshold = threshold_factor * np.max(averaged_signal)
    new_peaks = np.where(averaged_signal > threshold)[0]
    picos.extend(new_peaks) #se guardan los nuevos en picos
    
    # Eliminar los datos más antiguos del búfer
    ecg_buffer = ecg_buffer[len(data):]


#principal
# Configuración en la visualización
VentanaTiempo = 10   # Define la ventana de tiempo que si visualiza en tiempo real
TiempoFinal = 20    # Define el tiempo total de adquisición 
# Configuración de la figura
plt.ion() 
figura1 = plt.figure()
figura1.suptitle('Gráfica en tiempo real', fontsize='16', fontweight='bold')
plt.xlabel('Tiempo (s)', fontsize='14')
plt.ylabel('Amplitud', fontsize='14')
plt.axes().grid(True)

#Flag para controlar el tiempo que corre el codigo 
run=True

# Lista para guardar datos Tiempo y Amplitud
timepoints = []
ydata = []
filtrado = []

# Configuración de la curva
line1, = plt.plot(ydata, linestyle='-')
line2, = plt.plot(ydata, linestyle='-')

plt.xlim([0,VentanaTiempo])

# Parámetros del filtro pasabanda
fs = 9600  # Frecuencia de muestreo en Hz
f1 = 5.0  # Frecuencia de corte inferior en Hz
f2 = 15.0  # Frecuencia de corte superior en Hz
order = 4  # Orden del filtro

# Diseñar el filtro pasabanda
nyquist = 0.5 * fs
normalized_f1 = f1 / nyquist
normalized_f2 = f2 / nyquist
b, a = sp.signal.butter(order, [normalized_f1, normalized_f2], btype='band')

# Configuración del algoritmo de Pan-Tompkins
n = 10  # Longitud de la ventana de promedio móvil
m = int(0.150 * fs)  # Longitud de la ventana de promedio móvil (150 ms)
threshold_factor = 0.01  # Factor para calcular el umbral adaptativo (10% del máximo)

# Inicializar variables
ecg_buffer = np.zeros(2000)  # Búfer para almacenar los últimos 2000 puntos de ECG
picos=[]


start_time = time()

try:
    while run:
        # Leer una línea completa de datos hasat encontrar \n
        linea = ard.readline().decode().strip()

        picos = pam_tom(linea)

        # Se asignan los datos a las listas para graficar
        ydata.append(linea)
        timepoints.append(time()-start_time)
        current_time = timepoints[-1]
        
        # Se actutaliza los datos en la grafica 
        line1.set_xdata(timepoints)
        line1.set_ydata(ydata)
        
        # Se actutaliza los datos en la grafica 
        line2.set_xdata(timepoints)
        line2.set_ydata(filtrado)
        
        plt.ylim([min(ydata)-5,max(ydata)+5])
        # Se actualiza la ventan de observación de la gráfica
        if current_time > VentanaTiempo:
            plt.xlim([current_time-VentanaTiempo,current_time])
            
        # La ejecución termina cuando el tiempo de ejecución llega al límite
        if timepoints[-1] > TiempoFinal: run=False        
        
except KeyboardInterrupt:
    # Manejar la interrupción del teclado para detener la adquisición de datos
    ard.close()
