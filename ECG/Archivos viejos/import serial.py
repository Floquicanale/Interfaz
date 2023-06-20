import serial
import time

class Prueba_Mila():

    def connect_arduino(self):
        self.m=0
        try: 
            self.serialArduinoA = serial.Serial(
                'COM5',
                9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=None
            )
            print("Arduino connected")
            self.updateStreamArd()
        except serial.SerialException:
            print("no pude conectarme")
            pass
           
    '''
    def get_data(self):
        while len(self.x_array) < 2000:
            self.serialArduinoA.write(b's')
            valSignal = self.serialArduinoA.read(size=200)
            for i in range(0, len(valSignal) - 1, 2):
                val2 = ord(valSignal[i:i+1])
                val3 = ord(valSignal[i+1:i+2])
                val4 = val2 * 256 + val3
                val5 = (val4 * 5) / 1024
                self.valSignalP_ARD.append(val5)
                self.x_array.append((self.m/self.sample_rate))
                self.m += 1
            #self.data_updated.emit(self.x_array, self.valSignalP_ARD, self.RR_Average1)
        #self.flush_buffer_to_file()
        return self.valSignalP_ARD

    '''
    def updateStreamArd(self):
        self.valSignalP_ARD = []
        print("por mandar la señal")
        self.serialArduinoA.write(b's')
        print("mande la señal")

        response = self.serialArduinoA.readline().decode().strip()
        print("Received from Arduino:", response)
        '''
        try:
            valSignal = self.serialArduinoA.read(size=200)
        except Exception as e:
            print("Error:", e)
        
        for i in range(0, len(valSignal) - 1, 2):
            print("entre al for")
            val2 = ord(valSignal[i:i+1])
            val3 = ord(valSignal[i+1:i+2])
            val4 = val2*256+val3
            self.valSignalP_ARD.append(val4)
            val5 = (val4 * 5)/1024 # Paso el valor a volts
            self.valSignalP_ARD.append(val5)
        print("sali del for")
        return self.valSignalP_ARD
        '''
        
    
start = time.time()
print("empiezo")
stop = 1000+start
Prueba = Prueba_Mila()
Prueba.connect_arduino()
'''
while ((time.time()-stop)<0):
    data = Prueba.connect_arduino()
    print(data)
'''