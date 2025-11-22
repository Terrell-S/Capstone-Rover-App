#ifndef NAV_FUNCTIONS_H    
#define NAV_FUNCTIONS_H   
#include <Arduino.h> 

//Pin map
#define EncoderPinA 18
#define EncoderPinB 21
#define DirL        27
#define DirR        26
#define EnablePinR  25
#define EnablePinL  14

//test functions
void turn(int angle, float vel, float speedPct);
float metersFromCounts(long counts);
void setMotorPercent(int pwmPin, int dir, float speedPct=0);

#endif // NAV_FUNCTIONS_H