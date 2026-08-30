void setup() {
  Serial.begin(9600);

}

int contador = 0;
void loop() {
  contador ++;
  delay(2000);
  Serial.println(analogRead(A0));
}
