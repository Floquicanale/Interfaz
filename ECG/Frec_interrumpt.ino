#include <TimerThree.h>

void setup() {
  Serial.begin(9600);
  Timer3.initialize(4000);  // 250Hz (250 muestras por segundo --> muestreo cada 4000 us)
  Timer3.attachInterrupt(Muestreo); 
}

void loop() {
  // Tu código principal aquí
}

void Muestreo() {
  int valorA0 = analogRead(A0);
  Serial.println(valorA0);
}