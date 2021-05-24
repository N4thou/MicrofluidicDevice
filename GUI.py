################################################################################################################
##########################################Microfluidic device Code v1.0#########################################
############################################Code Made By Nathanael.T############################################
################################################################################################################

################################Libraries###########################################
import FluidController
import sys
import tkinter
from tkinter import *
from time import sleep
import _thread
import serial


################################Application#############################################

class Application(Frame): #main application for the frame

    def __init__(self,master):
        master.title('ProtheusMaker')

        #windows
        #master.iconbitmap(default='logo.ico')

        #windows
        if (sys.platform.startswith('win')): 
            master.iconbitmap('logo.ico')
        else:
        #Linux
            logo = PhotoImage(file='logo.png')
            master.call('wm', 'iconphoto', master._w, logo)
        
        self.screenwidth, self.screenheight = root.winfo_screenwidth(), root.winfo_screenheight()
        master.geometry("%dx%d+0+0" % (self.screenwidth, self.screenheight))
        Frame.__init__(self,master)

        self.grid()
        self.connected=False
        self.bussy = False
        self.create_widgets()

    def popupmsg(self,msg):      
        popup=Tk()        
        popup.geometry("280x75+0+0")
        popup.wm_title("Action required")
        w = Label(popup, text=msg)
        w.pack(side="top", fill="x",pady=10)
        B1=Button(popup,text=" Done ", command=popup.destroy)
        B1.pack()
        popup.mainloop()
    
    def flashingButton(self,Nb_Test):
        while (self.bussy==True):
            if (Nb_Test==1):
                app.button1["bg"]="mint cream"
            elif (Nb_Test==2):
                app.button2["bg"]="mint cream"
            elif (Nb_Test==8):
                app.button8["bg"]="mint red"
            sleep(.5)
            
            app.button1["bg"]="dodger blue"
            app.button2["bg"]="dodger blue"
            app.button8["bg"]="red"
            sleep(.5)

    def create_widgets(self):
        self.column_width = 10
        
        self.button0 = Button(self, text='Connect', command = self.pushButtonConnect, width = 2*self.column_width, bg="green")
        self.button0.grid(row=0, column=0, sticky = W)
        
        self.button1 = Button(self, text='Pumping(500ul)', command=self.PushButtonEnsayo1, width = self.column_width, bg="dodger blue")
        self.button1.grid(row=0, column=1, sticky = W)

        self.button2 = Button(self, text='Revers(500ul)', command=self.PushButtonEnsayo2, width = self.column_width, bg="dodger blue")
        self.button2.grid(row=1, column=1, sticky = W)

        self.button3 = Button(self, text='New experiement', command=self.PushButtonNew, width = self.column_width, bg="dodger blue")
        self.button3.grid(row=0, column=3, sticky = W)
        
        self.button8 = Button(self, text='camera', command=self.pushButtonCamera, width = self.column_width, bg="red")
        self.button8.grid(row=0, column=4, sticky = E)
        
        self.display_text = Text(self, width = 240, height =59)
        self.display_text.grid(row = 6, column =0, columnspan=10, sticky = W)

    def pushButtonConnect(self):
        if (self.connected == False):
            app.display_text.insert('end',"Connecting...\n")
            app.display_text.update_idletasks()
            pmaker.connect()
            app.display_text.delete('0.0','end')
            sleep(.5)
            app.display_text.insert('end',"*****************************CONNECTED*****************************\n")
            app.button0["text"]="Stop & Disconnect"
            app.button0["bg"]="red"
            app.connected=True
        else:
            pmaker.close()
            pmaker.connect()
            pmaker.close()
            if (self.bussy==True): 
                self.bussy=False
                app.display_text.insert('end',"\n****The Test was Interrupted*********************************************\n")
            app.display_text.insert('end',"\n****************************DISCONNECTED****************************\n")
            app.button0["text"]="Conect"
            app.button0["bg"]="green" 
            self.connected=False   
            app.display_text.update_idletasks() #Esto se hace por la linea rara que quedad del update del volumen

    def PushButtonNew(self):
        app.display_text.insert('end',"New window\n")

    def pushButtonCamera(self):
        app.display_text.insert('end',"Hello World\n")

    def PushButtonEnsayo1(self):
        self.PushButtonEnsayo(1)
     
    def PushButtonEnsayo2(self):
        self.PushButtonEnsayo(2)

    def PushButtonEnsayo(self,Nb_Test):
        if (self.connected == False):
            app.display_text.insert('end',"You are not connected\n")
        elif (self.bussy == True):
           app.popupmsg('Wait, an another process is still running!')
           #app.display_text.insert('end',"*Wait, an another process is still running!\n")
        else:
            self.bussy = True
            _thread.start_new_thread(self.flashingButton,(Nb_Test,))
            _thread.start_new_thread(self.Ensayo,(Nb_Test,))

    def Ensayo(self,Nb_Test):
        app.display_text.insert('end',"\n****Comenzando Ensayo**********************************************\n")
        app.display_text.update_idletasks()

##***************************************Protocols**********************************##

##****************************Options**********************************:
#        pmaker.MountSpetter(1,app)                         Motor   [Bomba=1]
#        pmaker.DismountSpetter(1,app)                      Motor   [Bomba=1]
        
#        pmaker.MoveStepper(1,1,10,250,app)                 Motor   [Bomba=1],Direcc[0,1], Steps   , Period(ms)
#        pmaker.MoveStepperFlujo(1,1,10,250,app)            Motor   [Bomba=1],Direcc[0,1], Vol[uL] , Flow(uL/s)
#        pmaker.MoveStepperFlujoUpDown(1,1,10,250,2,1,app)  Motor   [Bomba=1],Direcc[0,1], Vol[uL] , FlowNeto(uL/s), uLUp(uL), uLDown(uL)        

#        pmaker.Valves2Distr(Pos,app)                       Pos     [Buffer=1,FerrFerri=2, Sample=3]
#        pmaker.Medir(app)                                  Trigerea el potencioestato       
        
#        standar flow                                       2.5uL/s
        
#        Volumenes importantes a saber:
        Flow_uL_s=2.5
        
        Vol_Multiplexer_Chip=85 #uL (aprox)
        Vol_Chip=70
        
        Fe_Fer_Samplesize=90
        Blood_Samplesize=50     
        
########Ensayo1
        if (Nb_Test==1):    
            pmaker.MountSpetter(1,app)
            pmaker.MoveStepperFlujo(1,1,500,Flow_uL_s,app)
            pmaker.DismountSpetter(1,app)
            
########Ensayo2
        elif (Nb_Test==2):
            pmaker.MountSpetter(1,app)
            pmaker.MoveStepperFlujo(1,0,500,Flow_uL_s,app)
            pmaker.DismountSpetter(1,app)
            
        app.display_text.insert('end',"****Concluyendo Ensayo**********************************************\n")
        app.display_text.update_idletasks()
        
        self.bussy = False


#############################################main########################################################
pmaker = FluidController.Communication()
root=Tk()
app=Application(root) #creates the Frame
root.mainloop()
