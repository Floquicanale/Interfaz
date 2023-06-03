from ipaddress import summarize_address_range
import serial, time
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import csv


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
        '''
        max_val = max(max(result),-min(result))
        result = result/max_val
        '''

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

class Cardiac_Freq():
    def frequency(self, peaks, fs):
        distance = 0
        prom = 0
        frec=0
        if len(peaks[0])==0:
            pass
        else:
            for i in range(len(peaks[0])):
                print("entre al for")
                if(i+1<len(peaks[0])):
                    distance = peaks[0][i+1]-peaks[0][i]
                    prom += distance
            print(len(peaks[0]))
            prom = prom/(len(peaks[0])-1)
            print(prom)
            frec = 60/(prom/fs)
        
        return frec
    
    #def sound(self, peaks)
    '''
    def annotation(self, peaks, count)
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)

        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)

            # Write the first row (header) as it is
            writer.writerow(rows[0])

            # Write the second row with the annotations at the specific position
            second_row = rows[1]
            for i in range(len(peaks[0])):
                index = peaks[0][i]+count*500
                if second_row[index] == '': #Chequea que no haya nada en la columna
                    second_row[index] = 1
                

            writer.writerow(second_row)
            '''


'''
Codigo principal
Se usa un ciclo while para tomar datos de la señal a la cual se le aplica recursivamente Pan_Tom_QRS.
Primero hay que tomar un segmento de la señal y hacerle el procedimiento, este mismo cachito se guarda para recursividad.
La frecuencia de muestreo recomendada para el análisis de señales ECG suele estar en el rango de 200 a 500 Hz. 
La ventana de búfer debe ser lo suficientemente grande como para capturar un complejo QRS completo, incluyendo su parte ascendente y descendente. 
La duración típica de un complejo QRS está en el rango de 80 a 120 ms

'''
# Inicializar variables
ard = serial.Serial('COM5',9600)
fs = 250 #Hz

largo_ventana = fs*3
ecg_buffer = []  # Buffer para almacenar los puntos de ECG
output = []
picos = []
guardapicos=[]
timepoints = []
ydata=[]
threshold_factor = 0.09  # Factor para calcular el umbral adaptativo (10% del máximo)

start_time = time.time()
TiempoFinal = 100 # Define el tiempo total de adquisición en segundos
run = True

QRS_detector = Pan_Tom_QRS()
Cardio = Cardiac_Freq()

# Configuración de la figura
VentanaTiempo = 10
plt.ion()
figura1 = plt.figure()
figura1.suptitle('Gráfica en tiempo real', fontsize='16', fontweight='bold')
plt.xlabel('Tiempo (s)', fontsize='14')
plt.ylabel('Amplitud', fontsize='14')
plt.axes().grid(True)
# Configuración de la curva
line1, = plt.plot(ydata, linestyle='-')
#line2, = plt.plot(ydata, linestyle='-')

plt.xlim([0, VentanaTiempo])
n=0

try:
    while run:
        # Leer una línea completa de datos hasta encontrar \n
        linea = ard.readline().decode().strip()
        print(linea, "count: ", n)
        data = float(linea)
        ydata.append(data)
        timepoints.append(time.time() - start_time)
        current_time = timepoints[-1]

        #Primer llenado del buffer 5 segundos +2 segundos que se van a ir actualizando
        l = len(ecg_buffer)
        
        if(l<1750):
            ecg_buffer.append(data)

        #Cuando se actualiza el buffer se agregan 2 segundos de data
        elif(l>=1750):
            print("entre al if")
            print(ecg_buffer)
            output = QRS_detector.resolver(ecg_buffer, fs)

            #umbral adaptativo
            umbral = 0.7*max(output)
            print(umbral)
        
            # Busco los picos
            picos = sp.signal.find_peaks(output, height=umbral, distance=fs*0.67)
            print(picos)

            #Frecuencia cardiaca y esas cosas
            frecuencia = Cardio.frequency(picos, 250)
            print(frecuencia)
            #ACA HAY QUE CAMBIAR LO QUE MUESTRA EL DISPLAY
            #Cardiac_Freq.annotation() #anota en el csv que hubo un pico 

            ecg_buffer = ecg_buffer[500:] #elimino los primeros valores

        # Actualizar la gráfica
        '''
        line1.set_xdata(timepoints)
        line1.set_ydata(ydata)

        #line2.set_xdata(timepoints)
        #line2.set_ydata(output)

        plt.ylim([min(ydata) - 5, max(ydata) + 5])
        '''

        # Actualizar la ventana de observación de la gráfica
        if current_time > VentanaTiempo:
            plt.xlim([current_time - VentanaTiempo, current_time])

        if timepoints[-1] > TiempoFinal:
            run = False

        n+=1
        '''
        # Actualizar la gráfica
        plt.draw()
        plt.pause(0.001)
        '''


except KeyboardInterrupt:
    # Manejar la interrupción del teclado para detener la adquisición de datos
    ard.close()
    

