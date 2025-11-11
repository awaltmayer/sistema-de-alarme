#define TRIG 9
#define ECHO 10

void setup() {
  Serial.begin(9600);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
}

void loop() {
  long duration;
  int distance;

  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  duration = pulseIn(ECHO, HIGH);
  distance = duration * 0.034 / 2;  // Conversão em cm

  if (distance < 15) { // Limite de detecção (ajustável)
    Serial.println("ALERTA: movimento detectado");
    delay(2000);
  }

  delay(200);