#include <Wire.h>

#define Thermistorpin 0

float test=7;
int CAN;
float R0 = 10000;
float Rthm,T;
String temp;
char buff[10];
int buffzise=0;
//const float a=-6e-12 ,b=5e-07 ,c=-0.0112,d=92.268; //polynomial -5 to 100
const float A=3861.42059 ,B=0.02359875; //exp
void setup() {
  Wire.begin('T'); // join i2c bus (address optional for master)
  Serial.begin(115200);
  Wire.onRequest(requestEvent); // register event
}

void loop() {
  CAN=analogRead(Thermistorpin);
    
  Rthm=(1024*R0)/CAN-R0;
  
  //T=pow(Rthm,3)*a+pow(Rthm,2)*b+Rthm*c+d; //polynomial -5 to 100
  T=A/log(Rthm/B)-273.16; //exp
  //buffzise=sprintf(buff,"%f hello",test);
  temp = String(T);
  temp.toCharArray(buff,sizeof(buff));
  Serial.println(buff);
  delay(1000);
}

void requestEvent() {
  Wire.write(buff); // respond with message
}
