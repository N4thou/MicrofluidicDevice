#include <Stepper.h>
#include <Wire.h>


#define enPin 8
#define stepXPin 2 //X.STEP
#define dirXPin 5 // X.DIR
#define stepYPin 3 //Y.STEP
#define dirYPin 6 // Y.DIR
#define stepZPin 4 //Z.STEP
#define dirZPin 7 // Z.DIR
#define revo 25600
#define stepspeed 17000

Stepper Xaxis(revo, stepXPin, dirXPin );
Stepper Yaxis(revo, stepYPin, dirYPin ); // STEP, DIR
Stepper Zaxis(revo, stepZPin, dirZPin );

char buff[100];
int buffsize = 0;
float cmd;
bool block = false;
bool readend = false;

void setup() {
  Wire.begin(8);
  Wire.onReceive(receiveEvent);
  Serial.begin(9600);
  pinMode( enPin, OUTPUT);
  Xaxis.setSpeed(stepspeed);
  Yaxis.setSpeed(stepspeed);
  Zaxis.setSpeed(stepspeed);
  digitalWrite(enPin, HIGH);
}

void loop() {
  if (readend)
  {
    switch (buff[0])
    {
      case 'X':
        {
          cmd = atof(&buff[1]);
          digitalWrite(enPin, LOW);
          if (cmd >= 1)
          {
            for (int i = 0; i < cmd; i++) Xaxis.step(25600);
          }
          else if (cmd<1 and cmd>-1)
          {
            Xaxis.step(cmd * 25600); 
          }else if(cmd<=-1){
            for (int i = 0; i > cmd; i--) Xaxis.step(-25600);
          }
          Serial.write("ok");
          break;
        }
      case 'Y':
        {
          //Serial.print("Y");
          cmd = atof(&buff[1]);
          digitalWrite(enPin, LOW);
          if (cmd >= 1)
          {
            for (int i = 0; i < cmd; i++) Yaxis.step(25600);
          }
          else if (cmd<1 and cmd>-1)
          {
            Yaxis.step(cmd * 25600);
          }else if(cmd<=-1){
            for (int i = 0; i > cmd; i--) Yaxis.step(-25600);
          }
          Serial.write("ok");
          break;
        }
      case 'Z':
        {
          cmd = atof(&buff[1]);
          digitalWrite(enPin, LOW);
          if (cmd >= 1)
          {
            for (int i = 0; i < cmd; i++) Zaxis.step(25600);
            cmd = 0;
          }
          else if (cmd<1 and cmd>-1)
          {
            Zaxis.step(cmd * 25600);
          }else if(cmd<=-1){
            for (int i = 0; i > cmd; i--) Zaxis.step(-25600);
          }
          Serial.write("ok");
          break;
        }
      case 'B':
        {
          cmd = atoi(&buff[1]);
          if (cmd == 1)
          {
            block = true;
          } else if (cmd == 0) {
            block = false;
          }
          Serial.write("ok");
          break;
        }
      default:
        {
          Serial.println("error");
        }

    }
    cmd=0;
    if (!block)
    {
      digitalWrite(enPin, HIGH);
    } else
    {
      digitalWrite(enPin, LOW);
    }
    readend = false;
    buffsize = 0;
  }
}

void receiveEvent(int howMany) {
  while (Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character
    buff[buffsize] = c;
    //Serial.print(buff[buffsize]);
    if (c == '\n')
    {
      Serial.println("end");
      readend = 1;
    } else {
      buffsize++;
    }
  }
}
