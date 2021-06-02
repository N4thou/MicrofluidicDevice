################################################################################################################
##########################################Microfluidic device Code #############################################
############################################Code Made By Nathanael.T############################################
################################################################################################################

################################Libraries###########################################

import FluidController
import CameraController
import Camerarecord

import sys
from tkinter import filedialog
from tkinter import *
from time import sleep
import time
import _thread
import os
import cv2 as cv
from PIL import Image, ImageTk
import numpy as np
import serial
import serial.tools.list_ports

#############################Need for serial connection################################
def serialList(self):
    
    if (sys.platform == 'win32'):
        #Only on Windows
        for p in serial.tools.list_ports.grep("Arduino"):
            return p.device   
    else:
        #For Linux
        return '/dev/ttyS6'

################################Application#############################################

class Application(Tk): #main application for the frame

    def __init__(self):
        Tk.__init__(self)

        #specifiaction of the Frame
        self.screenwidth, self.screenheight = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.screenwidth, self.screenheight))

        #variable for experimentation
        self.Flow_uL_s=0.0
        self.Time=0
        self.direction=1
        self.Name="default"

        #variable for camera controle
        self.cameraAct=False
        self.camera=0
        self.rec=False
        self.frames=np.empty((10,10),None)
        self.img=np.empty((10,10),None)
        
        #variable for app controle
        self.expcheck=False
        self.grid()
        self.connected=False
        self.bussy = False
        self.fps=60
        self.delay=int(1000/self.fps)
        self.create_widgets()

        #variable for the connection
        self.com = serial.Serial() # create a Serial object
        self.com.port= serialList(self) #find the port
        self.com.baudrate= 115200   #set the speed
        self.com.timeout=1  #set the timeout (need to not be block when receiving data)
        self.Camera = CameraController.Communication(self.com)
        self.pmaker = FluidController.Communication(self.com)
        

    def popupmsg(self,msg): 
        #generate popup message      
        popup=Toplevel()        
        popup.geometry("280x75+0+0")
        popup.wm_title("Action required")
        w = Label(popup, text=msg)
        w.pack(side="top", fill="x",pady=10)
        B1=Button(popup,text=" Done ", command=popup.destroy)
        B1.pack()
        popup.mainloop()
    
    def flashingButton(self,Nb_Test): 
        #make button flashing
        while (self.bussy==True):
            if (Nb_Test==1):
                app.button1["bg"]="mint cream"
            elif (Nb_Test==2):
                app.button2["bg"]="mint cream"
            elif (Nb_Test==8):
                app.button7["bg"]="mint red"
            sleep(.5)
            
            app.button1["bg"]="dodger blue"
            app.button2["bg"]="dodger blue"
            app.button7["bg"]="red"
            sleep(.5)

    def create_widgets(self):
        self.column_width = 10
        
        self.button0 = Button(self, text='Connect', command = self.pushButtonConnect, width = 2*self.column_width, bg="green")
        self.button0.grid(row=0, column=0, sticky = W)
        
        #button used for debug
        self.button1 = Button(self, text='Revers(500ul)', command=self.PushButtonRevers, width = 2*self.column_width, bg="dodger blue")
        self.button1.grid(row=0, column=99, sticky = W)

        #button used for debug
        self.button2 = Button(self, text='Pumping(500ul)', command=self.PushButtonPumping, width = 2*self.column_width, bg="dodger blue")
        self.button2.grid(row=1, column=99, sticky = W)

        self.button3 = Button(self, text='New experiment', command=self.PushButtonNew, width = 2*self.column_width, bg="dodger blue")
        self.button3.grid(row=0, column=1, sticky = W)

        self.button5 = Button(self, text='Stop experiment', command=self.PushButtonStop, width = 2*self.column_width,state=DISABLED, bg="red")
        self.button5.grid(row=1, column=0, sticky = W)

        self.button6 = Button(self, text='move camera',command=self.pushButtonMoveCamera, width = 2*self.column_width, bg="orange")
        self.button6.grid(row=1, column=1, sticky = W)
        
        #button used for debug 
        self.button7 = Button(self, text='test record camera',command=self.pushButtonCamera, width = 2*self.column_width, bg="green")
        self.button7.grid(row=1, column=99, sticky = W)
        
        #Logs display
        self.display_text = Text(self, width = 120, height =59)
        self.display_text.grid(row = 2, column = 0,columnspan=5, sticky = W)

        #Video display
        self.display_video= Canvas(self,width = 580,height=480)
        self.display_video.grid(row=2,column=5,columnspan=5,sticky = W)
        


    def pushButtonConnect(self):
        if (self.connected == False):
            self.display_text.insert('end',"Connecting...\n")
            app.display_text.update_idletasks()
            if(self.connect()):
                self.display_text.delete('0.0','end')
                sleep(.5)
                self.display_text.insert('end',"*****************************CONNECTED*****************************\n")
                self.button0["text"]="Disconnect"
                self.button0["bg"]="red"
                self.connected=True
            else:
                self.display_text.insert('end',"No device found \n")
        else:
            self.rec=False
            self.button7["bg"]="green"
            
            if(self.cameraAct):
                self.vid.__del__()
                self.cameraAct=False
            self.pmaker.stop(app)
            self.disconnect()
            if (self.bussy==True): 
                self.bussy=False
                self.display_text.insert('end',"\n****The Test was Interrupted*********************************************\n")
            self.display_text.insert('end',"\n****************************DISCONNECTED****************************\n")
            self.button0["text"]="Conect"
            self.button0["bg"]="green" 
            self.connected=False   
            self.display_text.update_idletasks()

    def connect(self):
        if self.com.port==None:
            return False
        else:
            self.com.open() #start the connection
            return True

    def disconnect(self):
        if self.com.is_open:
            self.com.close()

    

####################################################Parameters########################################################

    def PushButtonNew(self):
        #self.display_text.insert('end',"New window\n")
        #Experiment_requirement=Tk()
        Experiment_requirement=Toplevel()       
        Experiment_requirement.geometry("380x130+0+0")
        Experiment_requirement.wm_title("Experiment_requirement")

        L1=Label(Experiment_requirement, text="Flow rate (ul/s)")
        L1.grid(row=1, column=0)

        L2=Label(Experiment_requirement, text="Time (s)")
        L2.grid(row=2, column=0)

        L3=Label(Experiment_requirement, text="Direction")
        L3.grid(row=4, column=0)

        L4=Label(Experiment_requirement, text="Experiment Name")
        L4.grid(row=0, column=0)

        self.e1 = Entry(Experiment_requirement)
        self.e1.grid(row=1,column=1)

        self.e2 = Entry(Experiment_requirement)
        self.e2.grid(row=2,column=1)

        self.e3 = Entry(Experiment_requirement)
        self.e3.grid(row=0,column=1)

        button8=Button(Experiment_requirement,text="START",width = self.column_width, command=lambda:[self.dir(),self.PushButtonStart(),Experiment_requirement.destroy()],bg="gray73")
        button8.grid(row=6,column=0)

        button9=Button(Experiment_requirement,text=" Save ",width = self.column_width,bg="gray73")
        button9.grid(row=6,column=2)
        button9.bind("<Button-1>", self.SaveEntry)
        button9.bind("<Return>", self.SaveEntry)

        self.button10=Button(Experiment_requirement,text="Pumping",width = self.column_width, command=self.pushButtonPumping,bg="gray73")
        self.button10.grid(row=4,column=1)

        self.button11=Button(Experiment_requirement,text="Revers",width = self.column_width, command=self.pushButtonRevers,bg="gray73")
        self.button11.grid(row=4,column=2)


        #Experiment_requirement.mainloop()

    def dir(self):
        self.path=filedialog.askdirectory()+"/%s" %(self.Name)
        self.pathframes=self.path+"/Frames"

    def SaveEntry(self,event):
        self.Flow_uL_s=float(self.e1.get())
        self.Time=int(self.e2.get())
        self.Name=self.e3.get()
        self.expcheck=True
        print(self.Name)
        print(self.Flow_uL_s)
        print(self.Time)
        print(self.direction)
        self.popupmsg("your entries have been saved")

    def pushButtonPumping(self):
        self.direction=0
        self.button10["bg"]="mint cream"
        self.button11["bg"]="gray73"
    
    def pushButtonRevers(self):
        self.direction=1
        self.button11["bg"]="mint cream"
        self.button10["bg"]="gray73"
    
    def PushButtonStart(self):
        if(self.expcheck==False):
            self.popupmsg('You have not enter parameters!\n')
        else: 
            os.mkdir(self.path)
            os.mkdir(self.pathframes)
            os.chdir(self.pathframes)
            #app.directory = app.directory +"/%s" %(self.Name)
            self.PushButtonExperiment(3)
            self.expcheck=False

    def PushButtonStop(self):
        self.rec=False
        self.button7["bg"]="green"
        self.cameraAct=False
        self.vid.__del__()
        self.pmaker.stop(app)
        self.bussy=False
        self.display_text.insert('end',"\n****The Test was Interrupted*********************************************\n")  
        self.display_text.update_idletasks() 
        print("test")
        self.button5.config(state=DISABLED)

###################################################################Camera################################################


#--------------part for the record---------------------------------#
    def pushButtonCamera(self):
        self.display_text.insert('end',"Cameras button\n")
        if(self.cameraAct==False):
            self.button7["bg"]="red"
            self.cameraAct=True
            self.vid=Camerarecord.MyVideoCapture(self.fps)
            self.starttime=time.time()
            self.rec=True
            self.update_frame()
        else:
            self.rec=False
            self.button7["bg"]="green"
            self.cameraAct=False
            self.vid.__del__()
            

    def update_frame(self):
        ret, frame = self.vid.get_frame()
        if ret:
            if self.rec:
                cv.imwrite(str(round(time.time()-self.starttime,5))+'.png',  cv.cvtColor(frame, cv.COLOR_RGB2BGR))
            self.image = Image.fromarray(frame)
            self.photo = ImageTk.PhotoImage(image=self.image)
            self.display_video.create_image(0, 0, image=self.photo, anchor='nw')
        
        if self.cameraAct:
            self.after(self.delay, self.update_frame)
            

#---------------part to move the camera-----------------------#

    def pushButtonMoveCamera(self):
        if (self.connected == False):
            self.display_text.insert('end',"You are not connected\n")
        else:
            self.cameraAct=True
            MovingCamera=Toplevel()
            MovingCamera.wm_title("MoveCamera")
            MovingCamera.protocol("WM_DELETE_WINDOW",self.killall)

            self.display_text.insert('end',"Cameras activate\n")
            self.display_text.update_idletasks()

            self.cameraAct=True
            self.vid=Camerarecord.MyVideoCapture(self.fps)
            self.starttime=time.time()
            self.rec=False
            self.update_frame()

            button12=Button(MovingCamera,text=" Quit ",command=lambda:[self.desactcam,self.vid.__del__(),MovingCamera.destroy()],width = self.column_width,bg="gray73")
            button12.grid(row=4,column=0)
        
            button13=Button(MovingCamera,text=" /\ (+y) ",command=self.moveFy,width = self.column_width,bg="gray73")
            button13.grid(row=0,column=1)
        
            button14=Button(MovingCamera,text="<= (-x)",command=self.moveBx,width = self.column_width,bg="gray73")
            button14.grid(row=1,column=0)

            button15=Button(MovingCamera,text="=> (+x)",command=self.moveFx,width = self.column_width,bg="gray73")
            button15.grid(row=1,column=2)
        
            button16=Button(MovingCamera,text="\/ (-y)",command=self.moveBy,width = self.column_width,bg="gray73")
            button16.grid(row=2,column=1)
        
            #button17=Button(MovingCamera,text="reset pos",command=self.rstPos,width = self.column_width,bg="gray73")
            #button17.grid(row=0,column=3)

            button18=Button(MovingCamera,text="x0.1",command=self.x01,width = self.column_width,bg="gray73")
            button18.grid(row=1,column=3)

            button19=Button(MovingCamera,text="x1",command=self.x1,width = self.column_width,bg="gray73")
            button19.grid(row=2,column=3)

            button20=Button(MovingCamera,text="x10",command=self.x10,width = self.column_width,bg="gray73")
            button20.grid(row=3,column=3)

            button21=Button(MovingCamera,text="x100",command=self.x100,width = self.column_width,bg="gray73")
            button21.grid(row=4,column=3)

            button22=Button(MovingCamera,text="Up (+z)",command=self.moveFz,width = self.column_width,bg="gray73")
            button22.grid(row=0,column=0)

            button23=Button(MovingCamera,text="Down (-z)",command=self.moveBz,width = self.column_width,bg="gray73")
            button23.grid(row=2,column=0)
    
    def moveFx(self):
        self.Camera.moveForwardX()

    def moveBx(self):
        self.Camera.moveBackwardX()

    def moveFy(self):
        self.Camera.moveForwardY()

    def moveBy(self):
        self.Camera.moveBackwardY()

    def moveFz(self):
        self.Camera.moveForwardZ()

    def moveBz(self):
        self.Camera.moveBackwardZ()
    
    def rstPos(self):
        self.Camera.resetPos()
    
    def x01(self):
        self.Camera.ChangeStepps(0.1)

    def x1(self):
        self.Camera.ChangeStepps(1)

    def x10(self):
        self.Camera.ChangeStepps(10)

    def x100(self):
        self.Camera.ChangeStepps(100)

    def desactcam(self):
        self.cameraAct=False

    def killall(self):
        self.desactcam
        self.vid.__del__()


#################################################Tests#####################################################################

    def PushButtonRevers(self):
        self.PushButtonExperiment(1)
     
    def PushButtonPumping(self):
        self.PushButtonExperiment(2)

    def PushButtonExperiment(self,Nb_Test):
        if (self.connected == False):
            self.display_text.insert('end',"You are not connected\n")
        elif (self.bussy == True):
           self.popupmsg('Wait, an another process is still running!')
        else:
            self.bussy = True
            _thread.start_new_thread(self.flashingButton,(Nb_Test,))
            _thread.start_new_thread(self.Ensayo,(Nb_Test,))

    def Ensayo(self,Nb_Test):
        self.button5.config(state=NORMAL)
        self.display_text.insert('end',"\n****Experiment start******************************************\n")
        self.cameraAct=True
        self.vid=Camerarecord.MyVideoCapture(self.fps)
        self.starttime=time.time()
        self.rec=True
        self.update_frame()
        self.display_text.update_idletasks()    
        
#-------------------------------------------Revers-----------------------------------------
        if (Nb_Test==1):    
            self.pmaker.MountSpetter(1,self)
            
            self.pmaker.MoveStepperFlujo(1,1,500,2.5,self)
            
            self.pmaker.DismountSpetter(1,self)
            
#-------------------------------------------Pumping---------------------------------------------
        elif (Nb_Test==2):
            self.pmaker.MountSpetter(1,self)
            self.pmaker.MoveStepperFlujo(1,0,500,2.5,self)
            self.pmaker.DismountSpetter(1,self)

#--------------------------------------------Experiment---------------------------------------------
        elif (Nb_Test==3):
            self.pmaker.MountSpetter(1,self)
            time.sleep(1)
            self.pmaker.MoveStepperPeriod(1,self.direction,self.Time,self.Flow_uL_s,self)
            time.sleep(1);
            self.pmaker.DismountSpetter(1,self)

        self.display_text.insert('end',"****Experiment Finish*****************************************\n")
        self.button5.config(state=DISABLED)
        self.display_text.update_idletasks()
        self.rec=False
        self.button7["bg"]="green"
        self.cameraAct=False
        self.vid.__del__()
        self.bussy = False

    def __del__(self):
        if(self.com.is_open):
            self.com.close()
        if(self.cameraAct):
            self.vid.__del__()


#############################################main########################################################
app=Application() #creates the Frame
app.directory=os.getcwd()
app.title('Microfluid_Ship')
#windows
if (sys.platform.startswith('win')): 
    app.iconbitmap('logo.ico')
#else:
#Linux
#    logo = PhotoImage(file='logo.png')
#    app.call('wm', 'iconphoto', app.window, logo)
os.chdir(app.directory)
app.mainloop()

