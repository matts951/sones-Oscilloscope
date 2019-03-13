# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 19:43:52 2019

@author: Matt A. Stedman

A program that houses a GUI and displays the output from the arduino in a human-readable graph.
The Arduino is acting as an oscilloscope, using a header for conversion.
"""

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use ("TkAgg")

import numpy as np

# Necessary for figures
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as anime
from scipy.interpolate import make_interp_spline, BSpline

# Necessary for aesthetics
from matplotlib import style
from setStyles import *

import time


# Initialise the python to arduino bridge
global SER
global DATA_SETS
global UPDATE_INTERVAL 
global COUNTER
global FPS

UPDATE_INTERVAL = "####"
ARD_CONNECT = False # Make this function work!
ARD_TRANSMIT = False
COUNTER = 0
FPS = 30


# Import the python to arduino communication
import serial

# Function to animate the oscilloscope graph -- MOVE TO SEPERATE FILE SOON
x = []
y = []

fig = Figure(figsize=(5, 5), dpi=100)
ax1 = fig.add_subplot(111)
ax1.set_xlim(-1, 1)
ax1.set_ylim(0, 255)
line, = ax1.plot(x, y, 'r')

UPDATE_INTERVAL = 10
def animate(i):
    # i is necessary for some unknown reason
    x, y, _ = grabData(i)
    global COUNTER, FPS, UPDATE_INTERVAL, ARD_TRANSMIT
    if COUNTER >= (1000 / FPS) and ARD_TRANSMIT:
        x = np.linspace(-1, 1, len(y))
        xx = np.linspace(-1, 1, 200)
        
        spl = make_interp_spline(x, y, k=3)
        yy = spl(xx)
        
        line.set_data(xx, yy)
        COUNTER = 0
    COUNTER = COUNTER + UPDATE_INTERVAL
    

## Main Osilloscope app ##
class appPlatform(tk.Tk): # This it just the Tkinter page initialisation
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "SOneS Oscilliscope")
        
        container = tk.Frame(self)  # SET THE WINDOW SIZE HERE?
        container.pack(side="top", fill="both", expand = True) # Pack just wedges all objects in the window        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        menu = tk.Menu(self)
        self.config(menu=menu)
        fileMenu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Export data")
        fileMenu.add_command(label="Import data")
        fileMenu.add_separator()
        fileMenu.add_command(label="Export as jpg")
        fileMenu.add_command(label="Export as video")
        fileMenu.add_separator()
        
        self.frames = {}
        
        for F in (StartPage, OscPage): ### Build up the pages that you want ###
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew") # Grid organises the objects based on location
        
        self.show_frame(StartPage)
        
    def show_frame(self, cont): #cont=controller
        frame = self.frames[cont]
        frame.tkraise()
    
class StartPage(tk.Frame):
    """ A welcome/start page, perhaps you can adjust settings or integrate/talk-to
    other products (like power supply)
    
    There may need to be an initialisation procedure to start speaking to the arduino/MCU """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        lTitle = ttk.Label(self, text="Welcome to the Open Source SOneS software.", font=LARGE_FONT)
        lDefin = ttk.Label(self, text="M.A.Stedman \n January 2019 \n Volunteer of the community.", font=SMALL_FONT)
        lTitle.pack(pady=30)
        lDefin.pack(pady=20)
        
        self.bStartText = ["Proceed without Connect", "Proceed"]

        self.v = tk.StringVar()
        self.v.set(self.bStartText[0])
        self.bConne = ttk.Button(self, text="Connect to Hardware", command=lambda: sendData.connect(self)) # Finish, connect to oscilloscope through PySerial
        self.bConne.pack()
        self.bStart = ttk.Button(self, textvariable=self.v, command=lambda: controller.show_frame(OscPage))
        self.bStart.pack()
        
        bQuit = ttk.Button(self, text="Quit", command=lambda: parent.destroy())
        bQuit.pack(side="bottom")
        
class OscPage(tk.Frame):
    ## Main page with graph, loads of buttons, some sub graphs, etc.
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        # Far left panel: home, reset, connect/disconnect, pop-outs #
        self.textL = "Connected to Arduino,\nrefresh rate: " + str(UPDATE_INTERVAL)
        ttk.Label(self, textvariable=self.textL).grid(row=0, sticky="n")
        self.homeButton = ttk.Button(self, text="Home",
                            command=lambda: controller.show_frame(StartPage))
        self.homeButton.grid(row=1, column=0, sticky="n")
        self.resetButton = ttk.Button(self, text="Reset")
        self.resetButton.grid(row=2, column=0, sticky="n")
        self.connectText = "Connect"
        self.connectButton = ttk.Button(self, text=self.connectText, command=sendData.beginComm)
        self.connectButton.grid(row=3, sticky="n")        
        self.popOutButton = ttk.Button(self, text="Pop Out")
        self.popOutButton.grid(row=4, sticky="n")
        
       
        # Left panel: oscilloscope display and labels #
        titleLabel = ttk.Label(self, text="SONES ver 0.1 Osc", font=LARGE_FONT)
        titleLabel.grid(row=0, column=1, sticky="n")
        subtitleLabel = ttk.Label(self, text="2 Channel, Multi-function", font=SMALL_FONT)
        subtitleLabel.grid(row=1, column=1, sticky="n")
        
        mplGRAPH = FigureCanvasTkAgg(fig, self)
        mplGRAPH.draw()
        mplGRAPH.get_tk_widget().grid(row=2, rowspan=4, column=1)
        mplGRAPH._tkcanvas.grid(row=2, rowspan=4, column=1)
        
        # Right Panel: Channel-set, trigger, menu (flexible) #  
        
        
        
        
    # Function that connects to available arduino and initialises
    # Set the serial output
        
class sendData():
### TO DO ###
## Set the UPDATE_INTERVAL and the SAMPLERATES ###
    def connect(win):
        global SER, ARD_CONNECT
        try:
            SER = serial.Serial('COM3', 115200, timeout=None)
            SER.flush()
            ARD_CONNECT = True
            time.sleep(1)
            sendData.holdComm()
            win.v.set(win.bStartText[1])
            ## win.bConne.bind("<Button-1>", sendData.disconnect)
        except:
            ARD_CONNECT = False
            print("Unable to connect")
            win.v.set(win.bStartText[0])
            ## win.bConne.bind("<Button-1>", sendData.connect)
            
    def FORCECONNECT():
        SER = serial.Serial('COM3', 115200, timeout=None)
        SER.flush()
        global ARD_CONNECT
        ARD_CONNECT = True
        
    def disconnect(win):
        global SER, ARD_CONNECT
        if ARD_CONNECT:
            sendData.holdComm()
            SER.close()
        ## win.bConne.bind("<Button-1>", sendData.connect)
        
        
    def beginComm():
        global SER, ARD_CONNECT
        if ARD_CONNECT:
            c = "BEGN"
            SER.write(c.encode())
    def setBUFFERLENGTH(n):
        global SER, ARD_CONNECT
        if ARD_CONNECT:
            c = "BUFF" + str(n)
            SER.write(c.encode())
    def holdComm():
        global SER, ARD_CONNECT
        if ARD_CONNECT:
            c = "HOLD"
            SER.write(c.encode())
    
def grabData(serOut):
## TO DO ##
## Design a function that buffers and edge-detects the data ##
    global SER, ARD_CONNECT, ARD_TRANSMIT
    if not ARD_CONNECT:
        return [0, 0], [0, 0], 0
    serOut = str(SER.readline())
    PREFIX = serOut[2:6]
    if PREFIX == "DATA":
        ARD_TRANSMIT = True
        serOut = serOut[6:]
        y = np.array(serOut.split(",")[1:-2]).astype(np.float)
        x = [0, 0]
        serOut = str("")
        return x, y, serOut
    elif PREFIX == "REFR":
        global UPDATE_INTERVAL
        try:
            UPDATE_INTERVAL = int(serOut[5:-4])
        except:
            UPDATE_INTERVAL = UPDATE_INTERVAL
## FIX THIS HERE MATT!!!     win.textL.set(str(UPDATE_INTERVAL))
        print(UPDATE_INTERVAL)
    elif PREFIX == "MESG":
        print(serOut[5:-4])
    ARD_TRANSMIT = False
    return [-1, 1], [-1, 1], 0

app = appPlatform()
## You can add init_func=fuctinon(){} to the FuncAnimation ##
ani = anime.FuncAnimation(fig, animate, interval=UPDATE_INTERVAL, blit=False) # Interval can be manually overriden
app.mainloop()

try:
    sendData.disconnect(0)
    print("Connection terminated")
except:
    pass