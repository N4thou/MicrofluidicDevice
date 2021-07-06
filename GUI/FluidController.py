################################################################################################################
###########################################Microfluidic device Code ############################################
############################################Code Made By Nathanael.T############################################
################################################################################################################

import numpy as np
from time import sleep
import serial
import serial.tools.list_ports
import math
from playsound import playsound
import _thread
import time
import sys
import subprocess


def serialList(self):
    
    if (sys.platform == 'win32'):
        #Only on Windows
        for p in serial.tools.list_ports.grep("Arduino"):
            return p.device   
    else:
        #For Linux
        return '/dev/ttyS6'

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
    def __init__(self,com):
        self.parametros = Parametros()
        self.com = com 
    
    def change_OS(self):
        self.parametros.Windows=abs(self.parametros.Windows-1)
        
    def WriteComand(self,cmd,app):
        cmd=cmd+'\n'
        print(cmd)
        for i in range(len(cmd)):
            self.com.write(cmd[i].encode('utf-8'))
        #self.ReadComand(app)
            
    def ReadComand(self,app):
        output_temp=''
        output='' 
        print("read")    
        i=0   
        self.com.read_until(expected='Done')

    def pause(self,app):
        self.WriteComand('WX',app)

    def stop(self,app):
        self.WriteComand('WZ',app)
        

# Bomba
                
    def MountSpetter(self,StepperMotor,app):
        cmd = 'W10 M1' #%(StepperMotor) 
        self.WriteComand(cmd,app)
    
    def DismountSpetter(self,StepperMotor,app):
        cmd = 'W11 M1' #%(StepperMotor) 
        self.WriteComand(cmd,app)        
        
    def MoveStepper(self,StepperMotor,Direction,Steps,Period,app):
        app.display_text.insert('end',"[+%ssteps] \n"%(Steps))
        app.display_text.update_idletasks()
        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor,Direction,Steps,Period)        
        self.WriteComand(cmd,app)
        
        
    def MoveStepperFlujo(self,StepperMotor,Direction,Vol_uL,Flow_uL_s,app):
        #move steppers depend on volum and flow
        if (StepperMotor==1):
            Steps=self.parametros.stepper1_StepsXuL*Vol_uL
        Time_s=Vol_uL/Flow_uL_s
        Period_ms=int((1000*Time_s)/Steps)
        Steps=int(Steps)
    
        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps,Period_ms)
        self.WriteComand(cmd,app)   
        self.ReportVolume(Vol_uL,Steps,Period_ms,Flow_uL_s,app)
        sleep(1)
        
    
    def MoveStepperPeriod(self,StepperMotor,Direction,Time_s,Flow_uL_s,app):
        #move steppers depend on Time and flow
        Vol_uL=Time_s*Flow_uL_s
        if (StepperMotor==1):
            Steps=self.parametros.stepper1_StepsXuL*Vol_uL
        Period_ms=int((1000*Time_s)/Steps)
        Steps=int(Steps)
    
        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps,Period_ms)   
        self.WriteComand(cmd,app)
        #_thread.start_new_thread(self.ReportVolume,(StepperMotor,Steps,Period_ms,Flow_uL_s,app,))
        self.ReportVolume(Vol_uL,Steps,Period_ms,Flow_uL_s,app)
        sleep(1)


    #move steppers depend on Time and flow for one fluid 
    def MoveStepperPeriodOneFluid(self,StepperMotor,Direction,Time_s,Flow_uL_s,app):

        #all the command sequence is writte in this methode
        
        Vol_uL=Time_s*Flow_uL_s
        if (StepperMotor==1):
            Steps=self.parametros.stepper1_StepsXuL*Vol_uL
        Period_ms=int((1000*Time_s)/Steps)
        Steps=int(Steps)
        
        cmd='W10 M1'
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps,Period_ms)   
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W11 M1'
        self.WriteComand(cmd,app)
        sleep(0.1)

        self.ReportVolumeOneFluid(Vol_uL,Time_s,Flow_uL_s,app)


    #move steppers depend on Time and flow with 2 fluid
    def MoveStepperPeriodTowFluid(self,StepperMotor,Direction,Time_s_1,Flow_uL_s_1,Time_s_2,Flow_uL_s_2,app):
        
        #fluid 1
        Vol_uL_1=Time_s_1*Flow_uL_s_1
        Steps_1=self.parametros.stepper1_StepsXuL*Vol_uL_1
        Period_ms_1=int((1000*Time_s_1)/Steps_1)
        Steps_1=int(Steps_1)

        #fluid 2
        Vol_uL_2=Time_s_2*Flow_uL_s_2
        Steps_2=self.parametros.stepper1_StepsXuL*Vol_uL_2
        Period_ms_2=int((1000*Time_s_2)/Steps_2)
        Steps_2=int(Steps_2)
        
        cmd='W10 M1'
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps_1,Period_ms_1)   
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd='W2 M1 A1000'
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps_2,Period_ms_2)   
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W11 M1'
        self.WriteComand(cmd,app)
        sleep(0.1)

        #_thread.start_new_thread(self.ReportVolume,(StepperMotor,Steps,Period_ms,Flow_uL_s,app,))
        self.ReportVolumeTowFluid(Vol_uL_1,Vol_uL_2,Time_s_1,Time_s_2,Flow_uL_s_1,Flow_uL_s_2,app)
        #sleep(1)


    #move steppers depend on Time and flow of tree fluid
    def MoveStepperPeriodTreeFluid(self,StepperMotor,Direction,Time_s_1,Flow_uL_s_1,Time_s_2,Flow_uL_s_2,Time_s_3,Flow_uL_s_3,app):
        
        
        #fluid 1
        if(Time_s_1!=0 and Flow_uL_s_1!=0):
            Vol_uL_1=Time_s_1*Flow_uL_s_1
            Steps_1=self.parametros.stepper1_StepsXuL*Vol_uL_1
            Period_ms_1=int((1000*Time_s_1)/Steps_1)
            Steps_1=int(Steps_1)
        else:
            Vol_uL_1=0.0
            Steps_1=0.0
            Period_ms_1=0
            Steps_1=0


        #fluid 2
        if(Time_s_2!=0 and Flow_uL_s_2!=0):
            Vol_uL_2=Time_s_2*Flow_uL_s_2
            Steps_2=self.parametros.stepper1_StepsXuL*Vol_uL_2
            Period_ms_2=int((1000*Time_s_2)/Steps_2)
            Steps_2=int(Steps_2)
        else:
            Vol_uL_2=0.0
            Steps_2=0.0
            Period_ms_2=0
            Steps_2=0

        #fluid 3
        if(Time_s_3!=0 and Flow_uL_s_3!=0):
            Vol_uL_3=Time_s_3*Flow_uL_s_3
            Steps_3=self.parametros.stepper1_StepsXuL*Vol_uL_3
            Period_ms_3=int((1000*Time_s_3)/Steps_3)
            Steps_3=int(Steps_3)
        else:
            Vol_uL_3=0.0
            Steps_3=0.0
            Period_ms_3=0
            Steps_3=0

        cmd='W10 M1'
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps_1,Period_ms_1)   
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd='W2 M1 A1000'
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps_2,Period_ms_2)   
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd='W2 M1 A500'
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W1 M%d D%d S%d T%d' %(StepperMotor, Direction,Steps_3,Period_ms_3)   
        self.WriteComand(cmd,app)
        sleep(0.1)

        cmd = 'W11 M1'
        self.WriteComand(cmd,app)
        sleep(0.1)

        #_thread.start_new_thread(self.ReportVolume,(StepperMotor,Steps,Period_ms,Flow_uL_s,app,))
        self.ReportVolumeTreeFluid(Vol_uL_1,Vol_uL_2,Vol_uL_3,Time_s_1,Time_s_2,Time_s_3,Flow_uL_s_1,Flow_uL_s_2,Flow_uL_s_3,app)
        #sleep(1)
    

    def ReportVolume(self,Vol_uL,Steps,Period_ms,Flow_uL_s,app):
        print("report")
        start_time = time.time()
        pause_time = 0.0
        #Vol_uL=Steps/self.parametros.stepper1_StepsXuL
        FlowingTime_s=Steps*Period_ms/1000
        elapsed_time = time.time() - start_time
        
        if hasattr(app, 'liquido'):
            app.display_text.insert('end',"*Inyectando %s" %(app.liquido))
        else:
            app.display_text.insert('end',"*Inyectando liquido")
        app.display_text.insert('end'," -> %suL a %suL/s \n"%(round(Vol_uL),Flow_uL_s))
        app.display_text.update_idletasks()
        
        fichier =open(app.path+"/result.txt",'w')
        while (elapsed_time<FlowingTime_s and app.bussy==True):
            while(app.pause==True):
                app.button8["bg"]="mint cream"
                sleep(0.5)
                app.button8["bg"]="orange"
                sleep(0.5)
                pause_time= time.time() - elapsed_time - start_time
            elapsed_time = time.time() - pause_time - start_time
            DepositedVolume=Vol_uL*int(round(elapsed_time))/FlowingTime_s
            app.display_text.delete("insert linestart", "insert lineend")
            app.display_text.insert('end',"**Vol depositado: %s uL"%(min(round(10*DepositedVolume)/10,round(Vol_uL))))
            fichier.write("%ss %s uL %s °C\n"%(round(elapsed_time,5),min(round(10*DepositedVolume)/10,round(Vol_uL)),app.output.decode("utf-8")))
            if app.bussy==True:
                app.display_text.update_idletasks()
                #print(app.bussy)
                time.sleep(.2)
        fichier.close()  
        app.display_text.update_idletasks()                
        app.display_text.delete("insert linestart", "insert lineend")
        app.display_text.update_idletasks()
        sleep(1.5)

    def ReportVolumeOneFluid(self,Vol_uL,FlowingTime_s,Flow_uL_s,app):
        print("report")
        start_time = time.time()
        pause_time = 0.0
        #Vol_uL=Steps/self.parametros.stepper1_StepsXuL
        #FlowingTime_s=Steps*Period_ms/1000
        elapsed_time = time.time() - start_time
        
        if hasattr(app, 'liquido'):
            app.display_text.insert('end',"*Inyectando %s" %(app.liquido))
        else:
            app.display_text.insert('end',"*Inyectando liquido")
        app.display_text.insert('end'," -> %suL a %suL/s \n"%(round(Vol_uL),Flow_uL_s))
        app.display_text.update_idletasks()
        
        fichier =open(app.path+"/result.txt",'w')
        while (elapsed_time<FlowingTime_s and app.bussy==True):
            while(app.pause==True):
                app.button8["bg"]="mint cream"
                sleep(0.5)
                app.button8["bg"]="orange"
                sleep(0.5)
                pause_time= time.time() - elapsed_time - start_time
            elapsed_time = time.time() - pause_time - start_time
            DepositedVolume=round(elapsed_time*Flow_uL_s,2)
            app.display_text.delete("insert linestart", "insert lineend")
            app.display_text.insert('end',"**Vol depositado: %s uL"%(min(round(DepositedVolume,2),round(Vol_uL))))
            fichier.write("%ss %s uL %s °C\n"%(round(elapsed_time,5),min(round(DepositedVolume,2),round(Vol_uL)),app.output.decode("utf-8")))
            if app.bussy==True:
                app.display_text.update_idletasks()
                #print(app.bussy)
                time.sleep(.2)
        fichier.close()  
        app.display_text.update_idletasks()                
        app.display_text.delete("insert linestart", "insert lineend")
        app.display_text.update_idletasks()
        sleep(1.5)

    def ReportVolumeTowFluid(self,Vol_uL_1,Vol_uL_2,FlowingTime_s_1,FlowingTime_s_2,Flow_uL_s_1,Flow_uL_s_2,app):
        print("report TowFluid")
        start_time = time.time()
        start_time_total = start_time

        pause_time = 0.0
        pause_time_total =0.0
        DepositedVolume_already=0.0

        Vol_uL=Vol_uL_1+Vol_uL_2
        Fluid2=False

        FlowingTime_s=FlowingTime_s_1+FlowingTime_s_2
        Flow_uL_s_current=Flow_uL_s_1
        elapsed_time = time.time() - start_time
        elapsed_time_total=time.time() - start_time_total
        
        if hasattr(app, 'liquido'):
            app.display_text.insert('end',"*Injection %s" %(app.liquido))
        else:
            app.display_text.insert('end',"*Liquid Injection")
        app.display_text.insert('end'," -> %suL at %suL/s and %suL at %suL/s\n"%(round(Vol_uL_1),Flow_uL_s_1,round(Vol_uL_2),Flow_uL_s_2))
        app.display_text.update_idletasks()
        
        fichier =open(app.path+"/result.txt",'w')
        while (elapsed_time_total<FlowingTime_s and app.bussy==True):
            while(app.pause==True):
                app.button8["bg"]="mint cream"
                sleep(0.5)
                app.button8["bg"]="orange"
                sleep(0.5)
                pause_time= time.time() - elapsed_time - start_time
                pause_time_total= pause_time_total + pause_time
            elapsed_time_total = time.time() - pause_time_total - start_time_total
            elapsed_time = time.time() - pause_time - start_time
            DepositedVolume=round(elapsed_time*Flow_uL_s_current,2)+DepositedVolume_already
            if(round(DepositedVolume)>= Vol_uL_1 and Fluid2 == False):
                Fluid2=True
                start_time = time.time()
                pause_time = 0.0
                DepositedVolume_already=DepositedVolume
                Flow_uL_s_current=Flow_uL_s_2
                app.display_text.insert('end',"Fluid 2")
                fichier.write("Fluid 2\n")
                sleep(2)
            app.display_text.delete("insert linestart", "insert lineend")
            app.display_text.insert('end',"**Vol depositado: %s uL"%(min(round(DepositedVolume,2),round(Vol_uL))))
            fichier.write("%ss %s uL %s °C\n"%(round(elapsed_time_total,5),min(round(DepositedVolume,2),round(Vol_uL)),app.output.decode("utf-8")))
            if app.bussy==True:
                app.display_text.update_idletasks()
                #print(app.bussy)
                time.sleep(.2)
        fichier.close()  
        app.display_text.update_idletasks()                
        app.display_text.delete("insert linestart", "insert lineend")
        app.display_text.update_idletasks()
        sleep(1.5)

    def ReportVolumeTreeFluid(self,Vol_uL_1,Vol_uL_2,Vol_uL_3,FlowingTime_s_1,FlowingTime_s_2,FlowingTime_s_3,Flow_uL_s_1,Flow_uL_s_2,Flow_uL_s_3,app):
        print("report TowFluid")
        start_time = time.time()
        start_time_total = start_time

        pause_time = 0.0
        pause_time_total =0.0
        DepositedVolume_already=0.0

        Vol_uL=Vol_uL_1+Vol_uL_2+Vol_uL_3

        Fluid2=False
        Fluid3=False
        
        FlowingTime_s=FlowingTime_s_1+FlowingTime_s_2+FlowingTime_s_3
        Flow_uL_s_current=Flow_uL_s_1
        elapsed_time = time.time() - start_time
        elapsed_time_total=time.time() - start_time_total
        
        if hasattr(app, 'liquido'):
            app.display_text.insert('end',"*Injection %s" %(app.liquido))
        else:
            app.display_text.insert('end',"*Liquid Injection")
        app.display_text.insert('end'," -> %suL at %suL/s and %suL at %suL/s and %sul at %suL/s\n"%(round(Vol_uL_1),Flow_uL_s_1,round(Vol_uL_2),Flow_uL_s_2,round(Vol_uL_3),Flow_uL_s_3))
        app.display_text.update_idletasks()
        
        fichier =open(app.path+"/result.txt",'w')
        while (elapsed_time_total<FlowingTime_s and app.bussy==True):
            while(app.pause==True):
                app.button8["bg"]="mint cream"
                sleep(0.5)
                app.button8["bg"]="orange"
                sleep(0.5)
                pause_time= time.time() - elapsed_time - start_time
                pause_time_total= pause_time_total + pause_time
            elapsed_time_total = time.time() - pause_time_total - start_time_total
            elapsed_time = time.time() - pause_time - start_time
            DepositedVolume=round(elapsed_time*Flow_uL_s_current,2)+DepositedVolume_already
            if(round(DepositedVolume)>= Vol_uL_1 and Fluid2 == False):
                Fluid2=True
                start_time = time.time()
                pause_time = 0.0
                DepositedVolume_already=DepositedVolume
                Flow_uL_s_current=Flow_uL_s_2
                app.display_text.insert('end',"Fluid 2")
                fichier.write("Fluid 2\n")
                sleep(2)
            if(round(DepositedVolume-Vol_uL_1)>= Vol_uL_2 and Fluid3 == False):
                Fluid3=True
                start_time = time.time()
                pause_time = 0.0
                DepositedVolume_already=DepositedVolume
                Flow_uL_s_current=Flow_uL_s_3
                app.display_text.insert('end',"Fluid 3")
                fichier.write("Fluid 3\n")
                sleep(2)
            app.display_text.delete("insert linestart", "insert lineend")
            app.display_text.insert('end',"**Vol depositado: %s uL"%(min(round(DepositedVolume,2),round(Vol_uL))))
            fichier.write("%ss %s uL %s °C\n"%(round(elapsed_time_total,5),min(round(DepositedVolume,2),round(Vol_uL)),app.output.decode("utf-8")))
            if app.bussy==True:
                app.display_text.update_idletasks()
                #print(app.bussy)
                time.sleep(.2)
        fichier.close()  
        app.display_text.update_idletasks()                
        app.display_text.delete("insert linestart", "insert lineend")
        app.display_text.update_idletasks()
        sleep(1.5)
        
