#ifndef NAV_FUNCTIONS_H    
#define NAV_FUNCTIONS_H   
#include <Arduino.h> 

//Pin map
#define EncoderPinA 18
#define EncoderPinB 21
#define ForwardPin  27
#define BackwardPin 26
#define EnablePin   25

//test functions
void turn(int angle, float vel, float speedPct);
float metersFromCounts(long counts);
void setMotorPercent(float speedPct);

#endif // NAV_FUNCTIONS_H