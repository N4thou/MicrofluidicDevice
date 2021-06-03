#include <Wire.h>

void setup() {
  Wire.setClock(400000);
  Wire.begin(); // join i2c bus (address optional for master)
  Serial.begin(115200);
}

char buff[100];
int sizebuff;

void loop() {
  if(Serial.available())
  {
    sizebuff=Serial.readBytes(buff,100);
    Wire.beginTransmission(buff[0]); // transmit to device #8
    for(int i=0;i<sizebuff;i++)
    {
      Wire.write(buff[i]);
      buff[i]=0;
    }
    Wire.endTransmission();    // stop transmitting 
  }
  //delay(500);
}
