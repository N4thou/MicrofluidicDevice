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
    switch(buff[0])
    {
      case 'G':
      {
        Wire.beginTransmission(8); // transmit to device #8
        for(int i=2;i<sizebuff;i++)
        {
          Wire.write(buff[i]);
        }
        Wire.endTransmission();    // stop transmitting 
        break;
      }
      case 'W':
      {
        Wire.beginTransmission(9); // transmit to device #8
        for(int i=0;i<sizebuff;i++)
        {
          Wire.write(buff[i]);
          Serial.println(buff[i]);
        }
        Wire.endTransmission();    // stop transmitting 
        break;
      }
    }
  }
  //delay(500);
}
