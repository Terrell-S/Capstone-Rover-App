#include <Arduino.h>
#include <nav_functions.h>

// Forward-declare ISR so attachInterrupt can see it
void IRAM_ATTR updateEncoder();

// ESP32 LEDC (PWM) settings
const int pwmChannel = 0;
const int pwmFreq    = 20000; // 20 kHz
const int pwmRes     = 8;     // duty 0..255

volatile long EncoderValue = 0;

const float COUNTS_PER_REV = 1200.0;
const float WHEEL_CIRCUMFERENCE_M = 0.2513;



void setup() {
  pinMode(ForwardPin, OUTPUT);
  pinMode(BackwardPin, OUTPUT);

  pinMode(EncoderPinA, INPUT_PULLUP);
  pinMode(EncoderPinB, INPUT_PULLUP);

  ledcAttachChannel(EnablePin, pwmFreq, pwmRes,pwmChannel);
  //ledcSetup(pwmChannel, pwmFreq, pwmRes); //outdated functions
  //ledcAttachPin(EnablePin, pwmChannel);

  attachInterrupt(digitalPinToInterrupt(EncoderPinA), updateEncoder, RISING);

  Serial.begin(9600);
  delay(200);
}



int pos = 0; // test line
long prevCount = 0;
int angles[3] = {30,-45, 60};
unsigned long lastTime = 0;
int thing = 1; // delay turns to every 2 seconds 
void loop() {
  // read encoder safely and print distance
  float speedPct = 15.0f;
  setMotorPercent(speedPct);     // e.g., +60% forward (use negative for reverse)
  noInterrupts();
  long count = EncoderValue;
  interrupts();

  unsigned long now = millis();
  unsigned long dt_ms = now - lastTime;
  if (dt_ms <= 0) dt_ms = 1;
  lastTime = now;

  Serial.print("prevcount: ");
  Serial.println(prevCount);
  Serial.print("count: ");
  Serial.println(count);

  long delta = count - prevCount;  // difference since last cycle
  prevCount = count;               // update for next loop


  //print results
  Serial.print("delta: ");
  Serial.println(delta);
  Serial.println(metersFromCounts(delta),6);
  Serial.print("dt: ");
  Serial.println(dt_ms);


  float velocity =  metersFromCounts(delta)/(dt_ms/1000.0f); //divide by 1000 so ms -> s


  // turn test code
  if(thing % 30 == 0){
    Serial.println("turn params: ");
    Serial.print("angle: ");
    Serial.println(angles[pos]);
    Serial.print("velocity: ");
    Serial.println(velocity,6);
    Serial.print("speed percent: ");
    Serial.println(speedPct);
    Serial.println("going to turn...");
    turn(angles[pos],velocity,speedPct);
    pos++;
    if (pos > 2) pos = 0;
  }

  thing++;
  delay(100);
}

void IRAM_ATTR updateEncoder() {
  // Quadrature direction from B at the instant A rises
  //if B is high, it is leading A, so reversing
  if (digitalRead(EncoderPinB) == HIGH) {
    EncoderValue--;
  } else {
    EncoderValue++;
  }
}
