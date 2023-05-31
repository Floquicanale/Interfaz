const int pinEntrada = A0;  // Pin de entrada analógica para la señal ECG
const int frecuenciaMuestreo = 250;  // Frecuencia de muestreo deseada en Hz
const unsigned long periodoMuestreo = 1000 / frecuenciaMuestreo;  // Periodo de muestreo en milisegundos

void setup() {
  Serial.begin(9600);
}

void loop() {
  static unsigned long ultimoTiempoMuestreo = 0;
  
  // Realizar el muestreo a la frecuencia deseada
  if (millis() - ultimoTiempoMuestreo >= periodoMuestreo) {
    ultimoTiempoMuestreo = millis();
    
    // Leer el valor analógico de la señal ECG
    int valor = analogRead(pinEntrada);
    
    // Enviar el valor leído a través del puerto serie
    Serial.println(valor);
}
