#include <nav_functions.h>

//test functions
const float WHEEL_SEPERATION = 0.251075;
const float COUNTS_PER_REV = 1200.0;
const float WHEEL_CIRCUMFERENCE_M = 0.2513;
void turn(int angle, float vel, float speedPct){
  if (vel == 0 || isnan(vel)) return; //can't turn if velocity is 0

  float velToPct = speedPct/vel; //conversion factor for velocity to speedPct
  float angle_rad = angle * PI / 180.0;
  float k = 0.5; // turn speed factor 0-1
  //dictate if turning left or right
  //get angeular velocity from difference in wheel speeds
  float Vr = vel * (1-k);
  float Vl = vel * (1+k);
  float w = (Vl-Vr)/WHEEL_SEPERATION;
  if(angle < 0){ //turn right
    Vr = vel * (1-k);
    Vl = vel * (1+k);
    w = (Vl-Vr)/WHEEL_SEPERATION;
    angle_rad *= -1;
  }
  else{
    Vr = vel * (1+k);
    Vl = vel * (1-k);
    w = (Vr-Vl)/WHEEL_SEPERATION;
  }
  //calculate how long difference is on 
  float t = angle_rad/w; 
  if(t < 0) t=t*-1;
  Serial.print("turn time: ");
  Serial.println(t);

  //set motors to turning speeds for duration then return them to normal
  setMotorPercent(Vr*velToPct); //just one motor for now
  delay((int)(t*1000)); //delay only takes ms in int
  setMotorPercent(speedPct);

  Serial.println("turn is complete");
}

float metersFromCounts(long counts) {
  return (counts / (float)COUNTS_PER_REV) * WHEEL_CIRCUMFERENCE_M;
}

// --- NEW: tiny helper for motor control (-100..+100 %) ---
void setMotorPercent(float speedPct) {
  // clamp
  if (speedPct >  100.0f) speedPct =  100.0f;
  if (speedPct < -100.0f) speedPct = -100.0f;

  // direction lines
  if (speedPct > 0) {
    digitalWrite(ForwardPin, HIGH);
    digitalWrite(BackwardPin, LOW);
  } else if (speedPct < 0) {
    digitalWrite(ForwardPin, LOW);
    digitalWrite(BackwardPin, HIGH);
    speedPct = -speedPct;  // use magnitude for duty
  } else {
    // coast
    digitalWrite(ForwardPin, LOW);
    digitalWrite(BackwardPin, LOW);
  }

  // map 0..100% -> 0..255 (8-bit)
  uint8_t duty = (uint8_t)(speedPct * 2.55f + 0.5f);
  ledcWrite(EnablePin, duty);
}