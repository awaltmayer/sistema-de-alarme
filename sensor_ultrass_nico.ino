#define TRIG 9
#define ECHO 10
#define BUZZER 8

long duracao;
int distancia;

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(BUZZER, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  duracao = pulseIn(ECHO, HIGH);
  distancia = duracao * 0.034 / 2;

  if (distancia < 30 && distancia > 0) {
    tone(BUZZER, 1000);  // Liga o buzzer com frequência de 1kHz
    Serial.println("1");
    delay(500);
    noTone(BUZZER);      // Desliga o buzzer
    delay(2000);         // Espera antes da próxima leitura
  } else {
    noTone(BUZZER);
  }
}
