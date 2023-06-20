import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

ard = serial.Serial('COM5', 9600)

# Parámetros del filtro pasabanda
fs = 9600  # Frecuencia de muestreo en Hz
f1 = 5.0  # Frecuencia de corte inferior en Hz
f2 = 15.0  # Frecuencia de corte superior en Hz
order = 4  # Orden del filtro

# Diseñar el filtro pasabanda
nyquist = 0.5 * fs
normalized_f1 = f1 / nyquist
normalized_f2 = f2 / nyquist
b, a = butter(order, [normalized_f1, normalized_f2], btype='band')

# Configuración del algoritmo de Pan-Tompkins
n = 10  # Longitud de la ventana de promedio móvil
m = int(0.150 * fs)  # Longitud de la ventana de promedio móvil (150 ms)
threshold_factor = 0.01  # Factor para calcular el umbral adaptativo (10% del máximo)

# Inicializar variables
ecg_buffer = np.zeros(2000)  # Búfer para almacenar los últimos 2000 puntos de ECG
picos = []

# Configuración en la visualización
VentanaTiempo = 10  # Define la ventana de tiempo que se visualiza en tiempo real
TiempoFinal = 50 # Define el tiempo total de adquisición

# Configuración de la figura
plt.ion()
figura1 = plt.figure()
figura1.suptitle('Gráfica en tiempo real', fontsize='16', fontweight='bold')
plt.xlabel('Tiempo (s)', fontsize='14')
plt.ylabel('Amplitud', fontsize='14')
plt.axes().grid(True)

# Flag para controlar el tiempo que corre el código
run = True

# Lista para guardar datos Tiempo y Amplitud
timepoints = []
ydata = []
filtrado = []

# Configuración de la curva
line1, = plt.plot(ydata, linestyle='-')
line2, = plt.plot(ydata, linestyle='-')

plt.xlim([0, VentanaTiempo])

start_time = time.time()

try:
    while run:
        # Leer una línea completa de datos hasta encontrar \n
        linea = ard.readline().decode().strip()
        print(linea)
        data = float(linea)

        # Se asignan los datos a las listas para graficar
        ydata.append(data)
        timepoints.append(time.time() - start_time)
        current_time = timepoints[-1]

        # Procesar los datos de ECG con el filtro pasabanda y el algoritmo de Pan-Tompkins
        ecg_buffer = np.append(ecg_buffer, data)
        ecg_buffer = ecg_buffer[1:]  # Eliminar los datos más antiguos del búfer

        # FILTRO PASABANDAS
        ecg_filtro = lfilter(b, a, ecg_buffer)
        filtrado.append(ecg_filtro[-1])  # Guardar el último valor filtrado

        # Derivada
        derivada = np.diff(ecg_filtro)

        # Cuadrado de la señal
        squared_signal = derivada ** 2

        # Promedio movil en una ventana de 150 ms
        averaged_signal = np.convolve(squared_signal, np.ones((m,)) / m, mode='valid')

        # Calcular el umbral adaptativo
        threshold = threshold_factor * np.mean(averaged_signal)

        # Detectar los picos QRS
        new_peaks = np.where(averaged_signal > threshold)[0]
        print("nuevo pico: ", new_peaks)
        picos.extend(new_peaks)  # Guardar los nuevos picos

        # Actualizar la gráfica
        line1.set_xdata(timepoints)
        line1.set_ydata(ydata)

        line2.set_xdata(timepoints)
        line2.set_ydata(filtrado)

        plt.ylim([min(ydata) - 5, max(ydata) + 5])

        # Actualizar la ventana de observación de la gráfica
        if current_time > VentanaTiempo:
            plt.xlim([current_time - VentanaTiempo, current_time])

        # La ejecución termina cuando el tiempo de ejecución llega al límite
        if timepoints[-1] > TiempoFinal:
            run = False

        # Actualizar la gráfica
        plt.draw()
        plt.pause(0.001)

except KeyboardInterrupt:
    # Manejar la interrupción del teclado para detener la adquisición de datos
    ard.close()
