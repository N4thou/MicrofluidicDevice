import numpy as np
from time import sleep
import serial
import serial.tools.list_ports
import math
from playsound import playsound
import _thread
import time
import subprocess

#import pygame

def serialList(self):
    
    if (self.parametros.Windows == 1):
        #Only on Windows
        for p in serial.tools.list_ports.grep("Arduino"):
            return p.device   
    else:
        #For Linux
        return '/dev/ttyUSB0'

class Parametros():
    def __init__(self):
        #Servos
        self.servo_IDs=["Buffer","Fe-Fer","Sample", "Test"]
        self.servo1_pos=0
        self.servo2_pos=0
        self.servo1_posList=[105, 105, 15,180]  #this is disctaminated by the 3 wells to be accessed
        self.servo2_posList=[100, 15, 15,180]        #Steppers
            #Steper1:BombaRoja
        
        self.stepper1_umXpaso=1.7
        
        #Jeringa 5ml cristal
        self.stepper1_Rjeringa_um_5mL_cristal=5908.4732 # H(mm)*Pi*R(mm)^2=Vol(uL)
        self.stepper1_StepsXuL_jeringa_5mL_cristal=1E9/(self.stepper1_umXpaso*math.pi*self.stepper1_Rjeringa_um_5mL_cristal**2)
        
        #Jeringa 5ml plástico
        self.stepper1_Rjeringa_um_5mL_plastico=6148.5
        self.stepper1_StepsXuL_jeringa_5mL_plastico=1E9/(self.stepper1_umXpaso*math.pi*self.stepper1_Rjeringa_um_5mL_plastico**2)
        
        #Jeringa 1ml plástico
        self.stepper1_Rjeringa_um_1mL_plastico=4722.12
        self.stepper1_StepsXuL_jeringa_1m_plasticoL=1E9/(self.stepper1_umXpaso*math.pi*self.stepper1_Rjeringa_um_1mL_plastico**2)
        
        self.stepper1_StepsXuL=self.stepper1_StepsXuL_jeringa_5mL_plastico
        #Resto
        self.Windows = 1
        
class Communication():
    def __init__(self):
        self.parametros = Parametros()        

    def connect (self):
        self.com = serial.Serial() # Establish the connection on a specific port
        self.com.port= serialList(self)
        self.com.baudrate= 115200        
        self.com.open()
        #Windows        
        if (self.parametros.Windows == True):
            while not self.com.is_open and not self.com.readable():
                sleep(.5)

        self.com.flushInput()
        self.com.flushOutput()
        sleep(.8)

    def is_open (self):
        print(self.com.is_open)
        return self.com.is_open
    
    def change_OS(self):
        self.parametros.Windows=abs(self.parametros.Windows-1)
        
    def close(self):
        self.com.close()
        
    def WriteComand(self,cmd,app):
        cmd=cmd+'\n'
        print(cmd)
        for i in range(len(cmd)):
            self.com.write(cmd[i].encode('utf-8'))
        return self.ReadComand(app)
            
    def ReadComand(self,app):
        output_temp=''
        output=''        
        while True:
            temp = self.com.readline().decode('utf-8')
            #print(temp)
            output_temp=output_temp+temp
            print(output_temp)
            if ("Done" in output_temp):
                return output

# Bomba
                
    def MountSpetter(self,StepperMotor,app):
        cmd = 'W10 M%d' %(StepperMotor) 
        self.WriteComand(cmd,app)
    
    def DismountSpetter(self,StepperMotor,app):
        cmd = 'W11 M%d' %(StepperMotor) 
        self.WriteComand(cmd,app)        
        
    def MoveStepper(self,StepperMotor,Direction,Steps,Period,app):
        app.display_text.insert('end',"[+%ssteps] \n"%(Steps))
        app.display_text.update_idletasks()
        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor,Direction,Steps,Period)        
        self.WriteComand(cmd,app)
        
        
    def MoveStepperFlujo(self,StepperMotor,Direction,Vol_uL,Flow_uL_s,app):
        if (StepperMotor==1):
            Steps=self.parametros.stepper1_StepsXuL*Vol_uL
        Time_s=Vol_uL/Flow_uL_s
        Period_ms=int((1000*Time_s)/Steps)
        Steps=int(Steps)
    
        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps,Period_ms)   
        _thread.start_new_thread(self.ReportVolume,(StepperMotor,Steps,Period_ms,app,))
        self.WriteComand(cmd,app)
        sleep(1)
        
    def MoveStepperFlujoUpDown(self,StepperMotor,Direction,Vol_uL,Flow_uL_s,uL_Up,uL_Down,app):
        if (StepperMotor==1):
            Phantom_Steps=self.parametros.stepper1_StepsXuL*Vol_uL
            Total_Steps=self.parametros.stepper1_StepsXuL*Vol_uL*((uL_Up+uL_Down)/(uL_Up-uL_Down))
            Up_Steps=self.parametros.stepper1_StepsXuL*uL_Up
            Down_Steps=self.parametros.stepper1_StepsXuL*uL_Down
        Time_s=Vol_uL/Flow_uL_s
        Phantom_Period_ms=int((1000*Time_s)/Phantom_Steps)
        Period_ms=int((1000*Time_s)/Total_Steps)
        Performed_Steps=0
        Up_resto=0
        Down_resto=0
        _thread.start_new_thread(self.ReportVolume,(StepperMotor,Phantom_Steps,Phantom_Period_ms,app,))   
        print('Steps')
        print(Total_Steps)
            
        while Performed_Steps<=Total_Steps:
            Up_Steps=Up_Steps+Up_resto
            cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,int(Up_Steps),Period_ms)
            self.WriteComand(cmd,app)
            Up_resto=Up_Steps-int(Up_Steps)
            
            Down_Steps=Down_Steps+Down_resto
            cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, abs(Direction-1),int(Down_Steps),Period_ms)
            self.WriteComand(cmd,app)
            Down_resto=Down_Steps-int(Down_Steps)
            
            Performed_Steps=Performed_Steps+Up_Steps+Down_Steps
        sleep(1)

    def ReportVolume(self,StepperMotor,Steps,Period_ms,app):
        start_time = time.time()
        if (StepperMotor==1):
            Vol_uL=Steps/self.parametros.stepper1_StepsXuL
            FlowingTime_s=Steps*Period_ms/1000
        elapsed_time = time.time() - start_time
        if hasattr(app, 'liquido'):
            app.display_text.insert('end',"*Inyectando %s" %(app.liquido))
        else:
            app.display_text.insert('end',"*Inyectando liquido")
        app.display_text.insert('end'," -> %suL a %suL/s \n"%(round(Vol_uL),round(10*Vol_uL/FlowingTime_s)/10))
        app.display_text.update_idletasks()
        
        while (elapsed_time<FlowingTime_s and app.bussy==True):
            elapsed_time = time.time() - start_time
            DepositedVolume=Vol_uL*int(round(elapsed_time))/FlowingTime_s
            app.display_text.delete("insert linestart", "insert lineend")
            app.display_text.insert('end',"**Vol depositado: %s uL"%(min(round(10*DepositedVolume)/10,round(Vol_uL))))
            if app.bussy==True:
                app.display_text.update_idletasks()
                #print(app.bussy)
                time.sleep(.2)  
        app.display_text.update_idletasks()                
        app.display_text.delete("insert linestart", "insert lineend")
        app.display_text.update_idletasks()
        sleep(1.5)

# Valves       

    def Valves2Distr(self,Pos,app):
        app.display_text.insert('end',"\n**Introduciendo %s \t \t \t"%(self.parametros.servo_IDs[Pos-1]))
        app.display_text.update_idletasks()
        self.MoveValves(1,self.parametros.servo1_posList[Pos-1],app)
        self.MoveValves(2,self.parametros.servo2_posList[Pos-1],app)
        
    def MoveValves(self,ServoMotor,Angle,app):
        cmd = 'W2 M%d A%d' %(ServoMotor,Angle)        
        self.WriteComand(cmd,app) 

    def ChangeValveManually(self,Liquido,app):
        app.liquido=Liquido
        _thread.start_new_thread(playsound,('cow.wav',))
        app.popupmsg('Cambiar válvula a %s' %Liquido)
        
# Medir

    def Medir(self,app):
        #subprocess.call([r'C:\Users\Fran\Drive\Protheus4\5_MedicionFlujo\Control_Bomba_valvulas\RunPSTraceOrder.bat'])
        sleep(1)
        cmd = 'W20'   
        self.WriteComand(cmd,app)
        
        app.display_text.update_idletasks()
        app.display_text.insert('end',"*Comenzando medida\n")
        app.display_text.update_idletasks()
#        app.popupmsg('Proceder con la medición')