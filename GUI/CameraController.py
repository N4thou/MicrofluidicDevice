################################################################################################################
##########################################Microfluidic device Code #############################################
############################################Code Made By Nathanael.T############################################
################################################################################################################

import serial

class Parameters:
    def __init__(self):
        self.stepps=1 # default stepps x1
        
class Communication:
    def __init__(self,com):
        self.parameter=Parameters()
        self.comCamera=com

    def moveForwardX(self):
        self.commande='G X'+str(self.parameter.stepps)
        self.sendCommande()

    def moveForwardY(self):
        self.commande='G Y'+str(self.parameter.stepps)
        self.sendCommande()

    def moveForwardZ(self):
        self.commande='G Z'+str(self.parameter.stepps)
        self.sendCommande()

    def moveBackwardX(self):
        self.commande='G X-'+str(self.parameter.stepps)
        self.sendCommande()

    def moveBackwardY(self):
        self.commande='G Y-'+str(self.parameter.stepps)
        self.sendCommande()

    def moveBackwardZ(self):
        self.commande='G Z-'+str(self.parameter.stepps)
        self.sendCommande()

    def sendCommande(self):
        self.comCamera.write((self.commande + '\n').encode('utf-8')) # Send g-code block

    def ChangeStepps(self,stepps):
        self.parameter.stepps=stepps





