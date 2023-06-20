import csv
import os
import sys
import serial
import time

def agregar_datos_csv(nuevos_datos, nombre_archivo, contador, delimiter=','):
    # Verificar si el archivo CSV ya existe y encontrar un nombre único
    nombre_base, extension = os.path.splitext(nombre_archivo)
    nombre_archivo = f'{nombre_base}{contador}{extension}'

    # Crear el archivo CSV y escribir los nuevos datos
    print(f"Creando archivo CSV: {nombre_archivo}")
    with open(nombre_archivo, 'a', newline='') as archivo_csv:
        if os.stat(nombre_archivo).st_size == 0:  # Verificar si el archivo está vacío
            cabecera = ['columna1', 'columna2', 'columna3']  # Reemplaza con los nombres de tus columnas
            escritor_csv = csv.writer(archivo_csv, delimiter=delimiter)
            escritor_csv.writerow(cabecera)
            print("adentro")

        escritor_csv = csv.writer(archivo_csv, delimiter=delimiter)
        escritor_csv.writerow(nuevos_datos)
    print("Datos agregados al archivo CSV.")

# En otra parte de tu código, obtén los nuevos datos
serial_port = serial.Serial('COM5', 9600)
contador=1
for i in range(6):
    time.sleep(4)
    if (i==4): contador=2
    line = serial_port.readline().decode('utf-8').strip()
    nuevos_datos = float(line)
    # Llama a la función para agregar los datos al archivo CSV
    agregar_datos_csv([nuevos_datos], 'datos.csv', contador, delimiter=';')
