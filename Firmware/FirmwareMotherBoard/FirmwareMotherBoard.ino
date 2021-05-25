/*
  Software serial multple serial test

 Receives from the hardware serial, sends to software serial.
 Receives from software serial, sends to hardware serial.

 The circuit:
 * RX is digital pin 10 (connect to TX of other device)
 * TX is digital pin 11 (connect to RX of other device)

 Note:
 Not all pins on the Mega and Mega 2560 support change interrupts,
 so only the following can be used for RX:
 10, 11, 12, 13, 50, 51, 52, 53, 62, 63, 64, 65, 66, 67, 68, 69

 Not all pins on the Leonardo and Micro support change interrupts,
 so only the following can be used for RX:
 8, 9, 10, 11, 14 (MISO), 15 (SCK), 16 (MOSI).

 created back in the mists of time
 modified 25 May 2012
 by Tom Igoe
 based on Mikal Hart's example

 This example code is in the public domain.

 */
#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX
SoftwareSerial mySerial2(5, 6);

char buff[100];
int sizebuff;
void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(115200);
  //while (!Serial) {
  //  ; // wait for serial port to connect. Needed for native USB port only
  //}


  //Serial.println("Goodnight moon!");

  // set the data rate for the SoftwareSerial port
  mySerial.begin(115200);
  //mySerial.println("Hello, world?");
  mySerial2.begin(115200);
}

void loop() { // run over and over
  int i=0;
  if(Serial.available()){
    sizebuff=Serial.readBytes(buff,100);
  
  if(buff[0]=='W')
  {
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
  /*
  //int i=0;
  if(Serial.available()){
    sizebuff=Serial.readBytes(buff,100);
  
  if(buff[0]=='G')
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
  if(mySerial2.available()){
    sizebuff=mySerial2.readBytes(buff,100);
    for(i=0;i<sizebuff-2;i++)
    {
     if(buff[i]!=0)
      {
        Serial.write(buff[i]);
        //Serial.print(buff[i]);
        buff[i]=0;
      }
    }
  }
  */
}
