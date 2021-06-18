#include <Wire.h>

void setup() {
  Wire.setClock(400000);
  Wire.begin(); // join i2c bus (address optional for master)
  Serial.begin(115200);
}

char buff[100];
int sizebuff;
char receive[10];
int receivesize;

void loop() {
  if(Serial.available())
  {
    sizebuff=Serial.readBytes(buff,100);
    if(buff[0]=='T')
    {
      Serial.println("requette");
      Wire.requestFrom(buff[0],5);
      while (Wire.available()) { // loop through all but the last
        char c = Wire.read(); // receive byte as a character
        receive[receivesize] = c;
        Serial.print(receive[receivesize]);
        if (c == '\n')
        {
          Serial.println("end");
        } else {
          receivesize++;
        }
      }
    }else{
      
      Wire.beginTransmission(buff[0]); // transmit to device
      for(int i=0;i<sizebuff;i++)
      {
        Wire.write(buff[i]);
        buff[i]=0;
      }
      Wire.endTransmission();    // stop transmitting 
    }
  }
  //delay(500);
}
