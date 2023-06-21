# ECG
En esta carpeta se encuentran los archivos de la interfaz de ECG, código de arduino para enviar datos, pruebas del algoritmo de Pan y Tompkins realizadas de manera offline y un archivo de datos tomados con el código propio de lectura de ECG (interfaz_ecg.py).
* Interfaz_ecg.py : archivo de python que crea y corre la interfaz de ECG, calcula frecuencia cardíaca y guarda los datos en un archivo csv cuando se le pide.
* Prueba_Pan_y_Tom.ipynb : archivo de Google Colab para la prueba del algoritmo de Pan y Tompkins con un archivo de ECG tomado de clase.
* Prueba_offline_datos1.ipynb: archivo de Google Colab para prueba del algoritmo de Pan y Tompkins con un archivo de ECG tomado por el código de python propio.
* datos1.csv : archivo de datos de prueba tomado con el código de python. Este archivo contiene valores de ECG, frecuencia y tiempo. Este ejemplo fue tomado con ruido como señal de entrada y es puramente demostrativo.
 # Algoritmo de Pam y Tompkins
 El algoritmo de Pan y Tompkins fue utilizado para la detección de picos en la onda de ECG en tiempo real para su posterior uso en el calculo de la frecuencia cardíaca.

Este algoritmo se puede dividir en varias etapas: Filtro pasabandas, Filtro derivativo, cuadrado e integrador de ventana móvil. 

## Filtro pasabandas
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
## Filtro derivativo
Metodología:
    Usamos un filtro derivativo de 5 puntos para obtener la pendiente de los picos. 
    El gráfico del filtro es lineal hasta los 30 Hz lo que lo 
    aproxima a una derivada ideal.

    Ecuacion recursiva del integrador:
      y(nT) = (1/8T)[-x(nT - 2T) - 2x(nT - T) + 2x(nT + T) + x(nT + 2T)]
    
      fuente: https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf
## Cuadrado
Metodología:
    Se eleva al cuadrado la señal para quedarnos con todos valores positivos

    Ecuacion:
      y(nT) = [x(nT)]^2
    
      fuente: https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf
## Integrador
Metodología:
    La idea es ver la duración de la onda. Por lo general el largo de la ventena debería ser
    aproximadamente el máximo valor del largo de un QRS. 
    Hay que buscarlo empíricamente, para el paper usado como bibliografía usan Fs = 200 Hz
    y la ventana de 30 muestras (150 ms). 

    Ecuacion de integrador con ventana móvil:
      y(nT) = 1/N [x(nT - (N-1)T) + x(nT - (N-2)T) + ... + x(nT)]
    
      fuente: https://www.robots.ox.ac.uk/~gari/teaching/cdt/A3/readings/ECG/Pan+Tompkins.pdf
# Resultados
## Usando archivo de la cátedra
<img width="685" alt="image" src="https://github.com/Floquicanale/TP-2-PSB/assets/92120272/b95e708e-c675-4296-a83a-9ca854234392">
<img width="672" alt="image" src="https://github.com/Floquicanale/TP-2-PSB/assets/92120272/aa8ce153-9392-421b-9279-3f02a6a5d297">
<img width="675" alt="image" src="https://github.com/Floquicanale/TP-2-PSB/assets/92120272/7f6d9a1a-43b3-4fc7-b491-91b2d041db42">
<img width="679" alt="image" src="https://github.com/Floquicanale/TP-2-PSB/assets/92120272/71dc4c31-3edc-4ab5-9c13-ebedc2bf7a94">



