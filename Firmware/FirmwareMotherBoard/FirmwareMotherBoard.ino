#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX
SoftwareSerial mySerial2(5, 6);

char buff[100];
int sizebuff;
void setup() {
  Serial.begin(115200); //serial connection to the computer

  mySerial.begin(115200); //serial connection to the pump

  mySerial2.begin(115200); //serial connection to the cameracontroller
  pinMode(4,OUTPUT);
  digitalWrite(4,HIGH);
}

//debug commande for the pump
//W1 M1 D1 S100 T350
void loop() { 
  int i=0;
  if(Serial.available()){
    sizebuff=Serial.readBytes(buff,100);
  
  if(buff[0]=='W')
  {
    if(buff[1]=='X')
    {
      digitalWrite(4,LOW);
      delay(0.1);
      digitalWrite(4,HIGH);
    }else{
    for(i=0;i<sizebuff;i++)
    {
      if(buff[i]!=0)
      {
        mySerial.write(buff[i]);
        //Serial.print(buff[i]);
        buff[i]=0;
      }
    }
    }
  }
  else if(buff[0]=='G')
  {
    for(i=0;i<sizebuff;i++)
    {
      if(buff[i]!=0)
      {
        mySerial2.write(buff[i]);
        //Serial.print(buff[i]);
        buff[i]=0;
      }
    }
  }
  }
  if(mySerial.available()){
    sizebuff=mySerial.readBytes(buff,100);
    for(i=0;i<sizebuff;i++)
    {
     if(buff[i]!=0)
      {
        Serial.write(buff[i]);
        //Serial.print(buff[i]);
        buff[i]=0;
      }
    }
  }else if(mySerial2.available()){
    sizebuff=mySerial2.readBytes(buff,100);
    for(i=0;i<sizebuff;i++)
    {
     if(buff[i]!=0)
      {
        Serial.write(buff[i]);
        //Serial.print(buff[i]);
        buff[i]=0;
      }
    }
  }
}
