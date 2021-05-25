################################################################################################################
##########################################Microfluidic device Code v1.3.1.1#####################################
############################################Code Made By Nathanael.T############################################
################################################################################################################

import serial
import time
import serial.tools.list_ports

def serialList():
    for p in serial.tools.list_ports.grep("CH340"): #Name of the board to controle the camera
        return p.device   

class Parameters:
    def __init__(self):
        self.stepps=1 # default stepps x1
        
class Communication:
    def __init__(self,com):
        self.parameter=Parameters()
        self.comCamera=com
        #self.comCamera=serial.Serial(serialList(),115200)


    #def connect(self):
    #    ports=serialList
    #    if(self.comCamera.is_open==False):
    #        self.comCamera=serial.Serial(serialList(),115200)
    #    self.comCamera.write(("\r\n\r\n").encode('utf-8'))
    #    time.sleep(2)   # Wait for grbl to initialize 
    #    self.comCamera.flushInput()  # Flush startup text in serial input
    #    self.commande="G17 G21 G91 G94 G54"
    #    self.sendCommande()

    #def disconnect(self):
    #    self.comCamera.close()

    def moveForwardX(self):
        self.commande='G0 X'+str(self.parameter.stepps)
        self.sendCommande()

    def moveForwardY(self):
        self.commande='G0 Y'+str(self.parameter.stepps)
        self.sendCommande()

    def moveForwardZ(self):
        self.commande='G0 Z'+str(self.parameter.stepps)
        self.sendCommande()

    def moveBackwardX(self):
        self.commande='G0 X-'+str(self.parameter.stepps)
        self.sendCommande()

    def moveBackwardY(self):
        self.commande='G0 Y-'+str(self.parameter.stepps)
        self.sendCommande()

    def moveBackwardZ(self):
        self.commande='G0 Z-'+str(self.parameter.stepps)
        self.sendCommande()
    
    def resetPos(self):
        self.commande='G90'
        self.sendCommande()
        self.commande='G0 X0 Y0 Z0'
        self.sendCommande()
        self.commande='G91'
        self.sendCommande()

    def sendCommande(self):
        self.comCamera.write((self.commande + '\n').encode('utf-8')) # Send g-code block to grbl
        grbl_out = self.comCamera.readline()
        print(grbl_out)

    def ChangeStepps(self,stepps):
        self.parameter.stepps=stepps

    #def __del__(self):
    #    if self.comCamera.is_open:
    #        self.disconnect()




