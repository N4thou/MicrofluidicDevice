//#include <MeOrion.h>
#include <EEPROM.h>
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////Inputs///////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <Servo.h>

Servo myservo1;
Servo myservo2;

//Stepper
const int buzzer = 9; //buzzer to arduino pin 9
const int Stepper1_Pul=7;
const int Stepper1_Dir=6; //define Direction pin
const int Stepper1_Ena=5; //define Enable Pin

//OTHERS
char cmd[64];
int8_t index=0;

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////StepperMoves////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//W1 M1 D1 S100 T350
void StepperMove(char *cmd){
  char * str;
  char * tmp;
  boolean Direction;
  int Period, Motor;
  unsigned long Steps;
  str = strtok_r(cmd, " ", &tmp);
  
  while (str != NULL) {
    str = strtok_r(0, " ", &tmp);
    if (str[0] == 'M')
      Motor = atof(str+1);
    else if (str[0] == 'D') 
      Direction = atoi(str + 1);
    else if (str[0] == 'S') 
      Steps = atoi(str + 1);
    else if (str[0] == 'T') 
      Period = atoi(str + 1);   //VER SI HAY UN ATOI DE UNISGEND LONG
  }

  switch (Motor){
    case 1: //BombaRoja
      if (Direction==0){
        digitalWrite(Stepper1_Dir,LOW);
      }else{
        digitalWrite(Stepper1_Dir,HIGH);
      }  
      for (int i=0; i<Steps; i++){  
        digitalWrite(Stepper1_Pul,LOW);
        digitalWrite(Stepper1_Pul,HIGH);
        delay(Period);
      }
      break;  
    }
}

void mountSpetter(char *cmd){
  char * str;
  char * tmp;
  int Motor;
  str = strtok_r(cmd, " ", &tmp);
  while (str != NULL) {
    str = strtok_r(0, " ", &tmp);
    if (str[0] == 'M')
      Motor = atoi(str+1);
  }
  
  switch (Motor){
    case 1: //Stepper1
      digitalWrite(Stepper1_Ena,HIGH);
      break;  
  }  
}

void dismountSpetter(char *cmd){
  char * str;
  char * tmp;
  int Motor;
  str = strtok_r(cmd, " ", &tmp);
  while (str != NULL) {
    str = strtok_r(0, " ", &tmp);
    if (str[0] == 'M')
      Motor = atoi(str+1);
  }
  
  switch (Motor){
    case 1: //Stepper1
      digitalWrite(Stepper1_Ena,LOW);
      break;  
  }  
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////ServoMoves/////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void ServoMove(char *cmd){
  char * str;
  char * tmp;
  int Angle, Motor;
  str = strtok_r(cmd, " ", &tmp);
  while (str != NULL) {
    str = strtok_r(0, " ", &tmp);
    if (str[0] == 'M')
      Motor = atof(str+1);
    else if (str[0] == 'A') 
      Angle = atoi(str + 1);
  }
  
  switch (Motor){
    case 1: //Servo1
      myservo1.write(Angle);
      break;
    case 2:
      myservo2.write(Angle);
      break;  
  }
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////Others////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void Buzz(char *cmd) {
  char * str;
  char * tmp;
  int buzz_time_ms;
  str = strtok_r(cmd, " ", &tmp);
  while (str != NULL) {
    str = strtok_r(0, " ", &tmp);
    if (str[0] == 'T')
      buzz_time_ms = atof(str+1);
  }
  
  tone(buzzer, 1000, buzz_time_ms); // Send 1KHz sound signal...
  noTone(buzzer);     // Stop sound...
}
 
void initRobotSetup() {
  int i;
  syncRobotSetup();
  for (i = 0; i < 64; i++) {
    cmd[i] = EEPROM.read(i);
  }
}

void syncRobotSetup() {
  int i;
  for (i = 0; i < 64; i++)
    EEPROM.write(i, cmd[i]);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////W-code///////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void parseWcode(char * cmd)
{
  int code;
  code = atoi(cmd);
  switch (code) {
    case 1: //Stepper
      StepperMove(cmd);
      break;  
    case 2: //ServoMove
      ServoMove(cmd);
      break;
    case 10: //Stepper mount
      mountSpetter(cmd);
      break;
    case 11: //Stepper dismount
      dismountSpetter(cmd);
      break;
    case 12:
      Buzz(cmd);
      break;    
  }
}

void ReadAndRun_comand() {
  while (Serial.available()) {
    
    char inByte = Serial.read();
    
    if (inByte == '\n') {
      Serial.print(inByte);
      
      if (cmd[0] == 'W') {
        parseWcode(cmd + 1);
      }
      Serial.println("Done");
      index = 0;
      memset(cmd, 0, 64);
    } else {
      cmd[index++] = inByte;
      //Serial.print("debug");
      
    }
    
    if (index >= 63) {
      index = 0;
    }
  }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////SETUP AND LOOP///////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void setup() {
  //Servos
  myservo1.attach(3);  
  myservo2.attach(4);
  //Stepper
  pinMode (Stepper1_Pul, OUTPUT);
  pinMode (Stepper1_Dir, OUTPUT);
  pinMode (Stepper1_Ena, OUTPUT);
  //digitalWrite(Stepper1_Ena,HIGH);
    
  Serial.begin(115200);
  initRobotSetup();
  pinMode(buzzer, OUTPUT); 
  //goHome();
}

void loop() {
  if (Serial.available()) {
    ReadAndRun_comand();
  }
}