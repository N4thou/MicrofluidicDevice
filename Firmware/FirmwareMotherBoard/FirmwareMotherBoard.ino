#include <Wire.h>
const int interruptpin=3;
bool check=true;
bool checkbuff=true;

void setup() {
  pinMode(interruptpin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptpin), startstop, RISING);
  Wire.setTimeout(3000);
  Wire.setClock(400000);
  Wire.begin(); // join i2c bus (address optional for master)
  Serial.begin(115200);
}

char buff[64];
int sizebuff;
char receive[10];
int receivesize;

void loop() {
  if(Serial.available())
  {
    sizebuff=Serial.readBytesUntil('\n',buff,64);
    //Serial.println(buff);
    if(buff[0]=='T')
    {
      //Serial.println("requette");
      Wire.requestFrom(buff[0],5);
      while (Wire.available()) { // loop through all but the last
        char c = Wire.read(); // receive byte as a character
        receive[receivesize] = c;
        Serial.print(receive[receivesize]);
        if (c == '\n')
        {
          //Serial.println("end");
        } else {
          receivesize++;
        }
      }
    }else{
      
      Wire.beginTransmission(buff[0]); // transmit to device
      for(int i=0;i<sizebuff;i++)
      {
        Wire.write(buff[i]);
        //Serial.print(buff[i]);
        buff[i]=0;
      }
      Wire.write('\n');
      Wire.endTransmission();    // stop transmitting 
    }
  }
 //delay(500);
  if(check!=checkbuff)
  {
    checkbuff=check;
    if(check){
      Serial.print("Start");
    }else{
      Serial.print("Stop");
    }
  }
}

void startstop()
{
  check=!check;
}
