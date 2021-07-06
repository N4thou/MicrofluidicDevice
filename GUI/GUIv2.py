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

############################################Need for serial connection########################################
def serialList(self):
    
    if (sys.platform == 'win32'):
        #Only on Windows
        for p in serial.tools.list_ports.grep("Arduino"):
            return p.device   
    else:
        #For Linux
        return '/dev/ttyS6'

##############################################Application#####################################################

class Application(Tk): #main application for the frame

    def __init__(self):
        Tk.__init__(self)

        #specifiaction of the Frame
        self.screenwidth, self.screenheight = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (self.screenwidth, self.screenheight))

        #variable for experimentation
        #Fluid 1
        self.Flow_uL_s_1=0.0
        self.Time_1=0
        #Fluid 2
        self.Flow_uL_s_2=0.0
        self.Time_2=0
        #fluid 3
        self.Flow_uL_s_3=0.0
        self.Time_3=0

        self.direction=1 #direction of the pump
        self.Name="default" #name of the experiment

        #variable for camera controle
        self.cameraAct=False #check activation of camera
        self.rec=False #availability of the a frame
        self.frames=np.empty((10,10),None) #init for the frame record
        self.img=np.empty((10,10),None) #init for the img record
        self.pause=False 
        self.pausetime=0.0

        #variable for app controle
        self.expcheck=False #check if parameter are enter
        self.grid()
        self.connected=False
        self.bussy = False
        self.fps=60
        self.delay=int(1000/self.fps)
        self.output="temp"
        self.create_widgets()
        

        #variable for the connection
        self.com = serial.Serial() # create a Serial object
        self.com.port= serialList(self) #find the port
        self.com.baudrate= 115200   #set the speed
        self.com.timeout=1  #set the timeout (need to not be block when receiving data)
        self.Camera = CameraController.Communication(self.com)
        self.pmaker = FluidController.Communication(self.com)
        

    def popupmsg(self,msg): 
        #generate a popup message      
        popup=Toplevel()        
        popup.geometry("280x75+0+0")
        popup.wm_title("Action required")
        w = Label(popup, text=msg)
        w.pack(side="top", fill="x",pady=10)
        B1=Button(popup,text=" Done ", command=popup.destroy)
        B1.pack()

######################################################## Main Menu ###############################################################
    def create_widgets(self):
        self.column_width = 10
        
        self.button0 = Button(self, text='Connect', command = self.pushButtonConnect, width = 2*self.column_width, bg="green")
        self.button0.grid(row=0, column=0, sticky = W)
        
        #button used for debug
        #self.button1 = Button(self, text='Revers(500ul)', command=self.PushButtonRevers, width = 2*self.column_width, bg="dodger blue")
        #self.button1.grid(row=0, column=99, sticky = W)

        #button used for debug
        #self.button2 = Button(self, text='Pumping(500ul)', command=self.PushButtonPumping, width = 2*self.column_width, bg="dodger blue")
        #self.button2.grid(row=1, column=99, sticky = W)

        self.button3 = Button(self, text='New experiment', command=self.PushButtonNew, width = 2*self.column_width, bg="dodger blue")
        self.button3.grid(row=0, column=1, sticky = W)

        self.button5 = Button(self, text='Stop experiment', command=self.PushButtonStop, width = 2*self.column_width,state=DISABLED, bg="red")
        self.button5.grid(row=1, column=0, sticky = W)

        self.button6 = Button(self, text='move camera',command=self.pushButtonMoveCamera, width = 2*self.column_width, bg="orange")
        self.button6.grid(row=1, column=1, sticky = W)
        
        
        #button used for debug 
        #self.button7 = Button(self, text='test record camera',command=self.pushButtonCamera, width = 2*self.column_width, bg="green")
        #self.button7.grid(row=1, column=99, sticky = W)

        self.button8 = Button(self, text='Pause experiment', command=self.PushButtonPause, width = 2*self.column_width,state=DISABLED, bg="red")
        self.button8.grid(row=0, column=2, sticky = W)
        
        #Logs display
        self.display_text = Text(self)#, width = 120, height =59)
        self.display_text.grid(column = 0,columnspan=3,row = 2,rowspan=2, sticky = W)

        #Video display
        image_2 = ImageTk.PhotoImage(file="video_not_working.png")
        
        self.display_video= Canvas(self)#,width = 580,height=480)
        self.display_video.grid(row=2,column=5,columnspan=5,sticky = W)
        self.display_video.create_image(0, 0, image=image_2, anchor='nw')
        self.display_video.image=image_2

        #dashboard
        image_1 = ImageTk.PhotoImage(file="Microfluidic_device.png")

        self.dashboard= Canvas(self,width = 580,height=434)
        self.dashboard.grid(row=3,column=5,sticky = W)
        self.dashboard.create_image(0, 0, image=image_1, anchor='nw')
        self.dashboard.image=image_1
        self.idtext=self.dashboard.create_text(580/2,434/2,text=self.output,fill='red')






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
                self.update_temp() #start the aquisition of the temperature 
            else:
                self.display_text.insert('end',"No device found \n")
        else:
            self.rec=False
            #self.button7["bg"]="green"
            
            if(self.cameraAct):
                self.vid.__del__()
                self.cameraAct=False
            
            self.disconnect()
            if (self.bussy==True): 
                self.bussy=False
                self.pmaker.stop(app)
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

    

################################################### Parameters #######################################################

    def PushButtonNew(self):
        if (self.connected == False):
            self.display_text.insert('end',"You are not connected\n")
        else:
            Experiment_requirement=Toplevel()       
            Experiment_requirement.geometry("380x130+0+0")
            Experiment_requirement.wm_title("number of fluid")

            L1=Label(Experiment_requirement, text="How many fluid in the experiment ?")
            L1.pack()

            button8=Button(Experiment_requirement,text="1 fluid", command=lambda:[self.Pushbutton1exp(),Experiment_requirement.destroy()],bg="gray73")
            button8.pack()

            button9=Button(Experiment_requirement,text="2 fluid", command=lambda:[self.Pushbutton2exp(),Experiment_requirement.destroy()],bg="gray73")
            button9.pack()

            button10=Button(Experiment_requirement,text="3 fluid", command=lambda:[self.Pushbutton3exp(),Experiment_requirement.destroy()],bg="gray73")
            button10.pack()

#--------------------------------menus for 1 fluid-----------------------------------------#
    def Pushbutton1exp(self):
        one_fluid_experiment=Toplevel()       
        one_fluid_experiment.geometry("380x130+0+0")
        one_fluid_experiment.wm_title("one_fluid_experiment")

        L1=Label(one_fluid_experiment, text="Flow rate (ul/s)")
        L1.grid(row=1, column=0)

        L2=Label(one_fluid_experiment, text="Time (s)")
        L2.grid(row=2, column=0)

        L3=Label(one_fluid_experiment, text="Direction")
        L3.grid(row=4, column=0)

        L4=Label(one_fluid_experiment, text="Experiment Name")
        L4.grid(row=0, column=0)

        self.e1 = Entry(one_fluid_experiment)
        self.e1.grid(row=1,column=1)

        self.e2 = Entry(one_fluid_experiment)
        self.e2.grid(row=2,column=1)

        self.e3 = Entry(one_fluid_experiment)
        self.e3.grid(row=0,column=1)

        button8=Button(one_fluid_experiment,text="START",width = self.column_width, command=lambda:[self.PushButtonStart(3,one_fluid_experiment)],bg="gray73")
        button8.grid(row=6,column=0)

        button9=Button(one_fluid_experiment,text=" Save ",width = self.column_width,bg="gray73")
        button9.grid(row=6,column=2)
        button9.bind("<Button-1>", self.SaveEntry1)
        button9.bind("<Return>", self.SaveEntry1)

        self.button10=Button(one_fluid_experiment,text="Pumping",width = self.column_width, command=self.pushButtonPumping,bg="gray73")
        self.button10.grid(row=4,column=1)

        self.button11=Button(one_fluid_experiment,text="Revers",width = self.column_width, command=self.pushButtonRevers,bg="gray73")
        self.button11.grid(row=4,column=2)
        
#--------------------------------menus for 2 fluid-----------------------------------------#
    def Pushbutton2exp(self):
        tow_fluid_experiment=Toplevel()       
        tow_fluid_experiment.geometry("600x200+0+0")
        tow_fluid_experiment.wm_title("tow_fluid_experiment")

        #-------------------Fluid 1------------------------------#
        L1=Label(tow_fluid_experiment, text="Experiment Name")
        L1.grid(row=0, column=0)

        L2=Label(tow_fluid_experiment, text="Fluid 1")
        L2.grid(row=1, column=0)

        L3=Label(tow_fluid_experiment, text="Flow rate (ul/s)")
        L3.grid(row=2, column=0)

        L4=Label(tow_fluid_experiment, text="Time (s)")
        L4.grid(row=3, column=0)
        
        self.e1 = Entry(tow_fluid_experiment) #Flow rate
        self.e1.grid(row=2,column=1)

        self.e2 = Entry(tow_fluid_experiment) #Time
        self.e2.grid(row=3,column=1)

        self.e3 = Entry(tow_fluid_experiment) #Experiment Name
        self.e3.grid(row=0,column=1)

        #-------------Fluid 2-------------------#
        L6=Label(tow_fluid_experiment, text="=======>")
        L6.grid(row=3, column=3)

        L7=Label(tow_fluid_experiment, text="Fluid 2")
        L7.grid(row=1, column=4)

        L9=Label(tow_fluid_experiment, text="Flow rate (ul/s)")
        L9.grid(row=2, column=4)

        L10=Label(tow_fluid_experiment, text="Time (s)")
        L10.grid(row=3, column=4)

        self.e4 = Entry(tow_fluid_experiment) #Flow rate Fluid 2
        self.e4.grid(row=2,column=5)

        self.e5 = Entry(tow_fluid_experiment) #Time Fluid2
        self.e5.grid(row=3,column=5)

        #---------------------Save start dirrection------------------------#
        L6=Label(tow_fluid_experiment, text="==========================================================================")
        L6.grid(row=5, column=0,columnspan=6)

        L5=Label(tow_fluid_experiment, text="Direction")
        L5.grid(row=6, column=0)

        button8=Button(tow_fluid_experiment,text="START",width = self.column_width, command=lambda:[self.PushButtonStart(4,tow_fluid_experiment)],bg="gray73")
        button8.grid(row=8,column=0)

        button9=Button(tow_fluid_experiment,text=" Save ",width = self.column_width,bg="gray73")
        button9.grid(row=7,column=2)
        button9.bind("<Button-1>", self.SaveEntry2)
        button9.bind("<Return>", self.SaveEntry2)

        self.button10=Button(tow_fluid_experiment,text="Pumping",width = self.column_width, command=self.pushButtonPumping,bg="gray73")
        self.button10.grid(row=6,column=1)

        self.button11=Button(tow_fluid_experiment,text="Revers",width = self.column_width, command=self.pushButtonRevers,bg="gray73")
        self.button11.grid(row=6,column=2)

    def Pushbutton3exp(self):
        tree_fluid_experiment=Toplevel()       
        tree_fluid_experiment.geometry("1000x200+0+0")
        tree_fluid_experiment.wm_title("tree_fluid_experiment")

        #-------------------Fluid 1------------------------------#
        L1=Label(tree_fluid_experiment, text="Experiment Name")
        L1.grid(row=0, column=0)

        L2=Label(tree_fluid_experiment, text="Fluid 1")
        L2.grid(row=1, column=0)

        L3=Label(tree_fluid_experiment, text="Flow rate (ul/s)")
        L3.grid(row=2, column=0)

        L4=Label(tree_fluid_experiment, text="Time (s)")
        L4.grid(row=3, column=0)
        
        self.e1 = Entry(tree_fluid_experiment) #Flow rate
        self.e1.grid(row=2,column=1)

        self.e2 = Entry(tree_fluid_experiment) #Time
        self.e2.grid(row=3,column=1)

        self.e3 = Entry(tree_fluid_experiment) #Experiment Name
        self.e3.grid(row=0,column=1)

        #-------------Fluid 2-------------------#
        L6=Label(tree_fluid_experiment, text="=======>")
        L6.grid(row=3, column=3)

        L7=Label(tree_fluid_experiment, text="Fluid 2")
        L7.grid(row=1, column=4)

        L9=Label(tree_fluid_experiment, text="Flow rate (ul/s)")
        L9.grid(row=2, column=4)

        L10=Label(tree_fluid_experiment, text="Time (s)")
        L10.grid(row=3, column=4)

        self.e4 = Entry(tree_fluid_experiment) #Flow rate Fluid 2
        self.e4.grid(row=2,column=5)

        self.e5 = Entry(tree_fluid_experiment) #Time Fluid2
        self.e5.grid(row=3,column=5)

        #----------Fluid 3-----------------------#

        L11=Label(tree_fluid_experiment, text="=======>")
        L11.grid(row=3, column=6)

        L12=Label(tree_fluid_experiment, text="Fluid 3")
        L12.grid(row=1, column=7)

        L13=Label(tree_fluid_experiment, text="Flow rate (ul/s)")
        L13.grid(row=2, column=7)

        L14=Label(tree_fluid_experiment, text="Time (s)")
        L14.grid(row=3, column=7)

        self.e6 = Entry(tree_fluid_experiment) #Flow rate Fluid 3
        self.e6.grid(row=2,column=8)

        self.e7 = Entry(tree_fluid_experiment) #Time Fluid 3
        self.e7.grid(row=3,column=8)

        #---------------------Save start dirrection------------------------#
        L6=Label(tree_fluid_experiment, text="======================================================================================================================")
        L6.grid(row=5, column=0,columnspan=9)

        L5=Label(tree_fluid_experiment, text="Direction")
        L5.grid(row=6, column=0)

        button8=Button(tree_fluid_experiment,text="START",width = self.column_width, command=lambda:[self.PushButtonStart(5,tree_fluid_experiment)],bg="gray73")
        button8.grid(row=8,column=0)

        button9=Button(tree_fluid_experiment,text=" Save ",width = self.column_width,bg="gray73")
        button9.grid(row=7,column=2)
        button9.bind("<Button-1>", self.SaveEntry3)
        button9.bind("<Return>", self.SaveEntry3)

        self.button10=Button(tree_fluid_experiment,text="Pumping",width = self.column_width, command=self.pushButtonPumping,bg="gray73")
        self.button10.grid(row=6,column=1)

        self.button11=Button(tree_fluid_experiment,text="Revers",width = self.column_width, command=self.pushButtonRevers,bg="gray73")
        self.button11.grid(row=6,column=2)

    #selection of the directory to save the output
    def dir(self):
        self.path=filedialog.askdirectory()+"/%s" %(self.Name)
        self.pathframes=self.path+"/Frames"

    #saving for 1 fluid
    def SaveEntry1(self,event):
        temp_Flow_uL_s_1=self.e1.get()
        temp_Time_1=self.e2.get()
        #check if paramter are enter
        if temp_Flow_uL_s_1=='' or temp_Time_1=='' or temp_Time_1=='0' or temp_Flow_uL_s_1=='0':
            self.popupmsg("You have not enter all parameters or they are not valide !")
        else:
            self.Flow_uL_s_1=float(self.e1.get())
            self.Time_1=int(self.e2.get())
            self.Name=self.e3.get()
            self.expcheck=True
            print(self.Name)
            print(self.Flow_uL_s_1)
            print(self.Time_1)
            print(self.direction)
            self.popupmsg("your entries have been saved")

    #saving for 2 fluid
    def SaveEntry2(self,event):
        temp_Flow_uL_s_1=float(self.e1.get())
        temp_Time_1=int(self.e2.get())

        temp_Flow_uL_s_2=float(self.e4.get())
        temp_Time_2=int(self.e5.get())

        if temp_Flow_uL_s_1=='' or temp_Time_1=='' or temp_Time_1=='0' or temp_Flow_uL_s_1=='0' or temp_Flow_uL_s_2=='' or temp_Time_2=='' or temp_Time_2=='0' or temp_Flow_uL_s_2=='0':
            self.popupmsg("You have not enter all parameters or they are not valide !")
        else:
            self.Name=self.e3.get()

            self.Flow_uL_s_1=float(self.e1.get())
            self.Time_1=int(self.e2.get())

            self.Flow_uL_s_2=float(self.e4.get())
            self.Time_2=int(self.e5.get())
        
            self.expcheck=True

            print(self.Name)
            print(self.Flow_uL_s_1)
            print(self.Time_1)
            print(self.Flow_uL_s_2)
            print(self.Time_2)
            print(self.direction)
            self.popupmsg("your entries have been saved")

    #saving for 3 fluid
    def SaveEntry3(self,event):
        temp_Flow_uL_s_1=float(self.e1.get())
        temp_Time_1=int(self.e2.get())
        

        temp_Flow_uL_s_2=float(self.e4.get())
        temp_Time_2=int(self.e5.get())

        temp_Flow_uL_s_3=float(self.e6.get())
        temp_Time_3=int(self.e7.get())

        if temp_Flow_uL_s_1=='' or temp_Time_1=='' or temp_Flow_uL_s_2=='' or temp_Time_2=='' or temp_Flow_uL_s_3=='' or temp_Time_3=='':
            self.popupmsg("You have not enter all parameters or they are not valide !")
        else:
            self.Name=self.e3.get()

            self.Flow_uL_s_1=float(self.e1.get())
            self.Time_1=int(self.e2.get())

            self.Flow_uL_s_2=float(self.e4.get())
            self.Time_2=int(self.e5.get())

            self.Flow_uL_s_3=float(self.e6.get())
            self.Time_3=int(self.e7.get())

            self.expcheck=True
            print(self.Name)
            print(self.Flow_uL_s_1)
            print(self.Time_1)
            print(self.Flow_uL_s_2)
            print(self.Time_2)
            print(self.Flow_uL_s_3)
            print(self.Time_3)
            print(self.direction)
            self.popupmsg("your entries have been saved")

    def pushButtonPumping(self):
        self.direction=1
        self.button10["bg"]="mint cream"
        self.button11["bg"]="gray73"
    
    def pushButtonRevers(self):
        self.direction=0
        self.button11["bg"]="mint cream"
        self.button10["bg"]="gray73"
    
    def PushButtonStart(self,exp,window):
        if(self.expcheck==False):
            self.popupmsg('You have not enter or save parameters!\n')
        else:
            window.destroy()
            self.dir()
            os.mkdir(self.path)
            os.mkdir(self.pathframes)
            os.chdir(self.pathframes)
            self.PushButtonExperiment(exp)
            self.expcheck=False

    def PushButtonStop(self):
        self.rec=False
        #self.button7["bg"]="green"
        self.cameraAct=False
        self.vid.__del__()
        self.pmaker.stop(app)
        self.bussy=False
        self.display_text.insert('end',"\n****The Test was Interrupted*********************************************\n")  
        self.display_text.update_idletasks() 
        print("test")
        if(self.pause):
            self.PushButtonPause()
        self.button5.config(state=DISABLED)
        self.button8.config(state=DISABLED)
    
    def PushButtonPause(self):
        if not(self.pause):
            self.pmaker.pause(app) 
            self.rec=False
            self.pause=True
            self.button8["bg"]="orange"
            self.button8["text"]="resume"
            self.display_text.insert('end',"\n****The Test was paused*********************************************\n")
            self.display_text.update_idletasks()
        else:
            self.pausetime=time.time() - self.elapsedtime -self.starttime
            self.rec=True
            self.pmaker.pause(app)
            self.pause=False
            self.button8["text"]="Pause experiment"
            self.button8["bg"]="red"
            self.display_text.insert('end',"\n****The Test continue*********************************************\n")
            self.display_text.update_idletasks()

###################################################################Camera################################################


#--------------part for the record---------------------------------#
    def pushButtonCamera(self):
        self.display_text.insert('end',"Cameras button\n")
        if(self.cameraAct==False):
            #self.button7["bg"]="red"
            self.cameraAct=True
            self.vid=Camerarecord.MyVideoCapture(self.fps)
            self.starttime=time.time()
            self.rec=True
            self.update_frame()
        else:
            self.rec=False
            #self.button7["bg"]="green"
            self.cameraAct=False
            self.vid.__del__()
            

    def update_frame(self):
        ret, frame = self.vid.get_frame()
        if ret:
            if self.rec:
                self.elapsedtime=time.time()-self.starttime-self.pausetime
                cv.imwrite(str(round(self.elapsedtime,5))+'.png',  cv.cvtColor(frame, cv.COLOR_RGB2BGR))
            self.image = Image.fromarray(frame)
            self.photo = ImageTk.PhotoImage(image=self.image)
            self.display_video.create_image(0, 0, image=self.photo, anchor='nw')
        
        if self.cameraAct:
            self.after(self.delay, self.update_frame)
            

#---------------part to move the camera-----------------------#

    def pushButtonMoveCamera(self):
        if (self.connected == False):
            self.display_text.insert('end',"You are not connected\n")
        else :
            self.vid=Camerarecord.MyVideoCapture(self.fps)
            if self.vid.video_available==True:
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
            else:
                self.display_text.insert('end',"video source not available\n")

    
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

####################################################temperature############################################################
    def update_temp(self):
        if self.connected:
            self.com.write("T\n".encode('utf-8'))
            self.output=self.com.read(size=5)
            if(self.output.decode('utf-8')=="start"):
                print(self.output.decode('utf-8'))
            else:
                self.dashboard.itemconfigure(self.idtext, text=self.output)
            self.after(1000, self.update_temp)

#################################################Experiments###############################################################

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
            _thread.start_new_thread(self.Ensayo,(Nb_Test,))

    def Ensayo(self,Nb_Test):
        self.button8.config(state=NORMAL)
        self.button5.config(state=NORMAL)
        self.display_text.insert('end',"\n****Experiment start******************************************\n")
        self.cameraAct=True
        self.vid=Camerarecord.MyVideoCapture(self.fps)
        self.starttime=time.time()
        self.rec=True
        if(self.vid.video_available==True):
            self.update_frame()
            self.display_text.update_idletasks()
        else:
            self.popupmsg('/!\WARNNING/!\ The video source is not avaible the frames will not be record !')
        
#-------------------------------------------Revers-----------------------------------------
#usefull for debuging
        if (Nb_Test==1):    
            self.pmaker.MountSpetter(1,self)
            self.pmaker.MoveStepperFlujo(1,1,500,2.5,self)
            self.pmaker.DismountSpetter(1,self)
            
#-------------------------------------------Pumping---------------------------------------------
#usefull for debuging
        elif (Nb_Test==2):
            self.pmaker.MountSpetter(1,self)
            self.pmaker.MoveStepperFlujo(1,0,500,2.5,self)
            self.pmaker.DismountSpetter(1,self)

#--------------------------------------------Experiment---------------------------------------------
        #experiment with one fluid
        elif (Nb_Test==3):
            self.pmaker.MoveStepperPeriodOneFluid(1,self.direction,self.Time_1,self.Flow_uL_s_1,self)

        #expeiment with tow fluid
        elif (Nb_Test==4):
            self.pmaker.MoveStepperPeriodTowFluid(1,self.direction,self.Time_1,self.Flow_uL_s_1,self.Time_2,self.Flow_uL_s_2,self)

        #exeriment with tree fluid
        elif (Nb_Test==5):
            self.pmaker.MoveStepperPeriodTreeFluid(1,self.direction,self.Time_1,self.Flow_uL_s_1,self.Time_2,self.Flow_uL_s_2,self.Time_3,self.Flow_uL_s_3,self)

        self.display_text.insert('end',"****Experiment Finish*****************************************\n")
        self.button8.config(state=DISABLED)
        self.button5.config(state=DISABLED)
        self.display_text.update_idletasks()
        self.rec=False
        #self.button7["bg"]="green"
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

