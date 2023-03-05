# Schaltsimulator Main variables declarations

import threading
import configparser
from tkinter import *
import sys





''' ---------------------------- Raspberry PINS for Relais Switch ---------------------------- '''
relais1Pin = 6
relais2Pin = 5
relais3Pin = 27
relais4Pin = 4
relais5Pin = 25
relais6Pin = 24
relais7Pin = 23
relais8Pin = 22

if not "win" in sys.platform: #if on windows
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relais1Pin, GPIO.OUT)
    GPIO.setup(relais2Pin, GPIO.OUT)
    GPIO.setup(relais3Pin, GPIO.OUT)
    GPIO.setup(relais4Pin, GPIO.OUT)
    GPIO.setup(relais5Pin, GPIO.OUT)
    GPIO.setup(relais6Pin, GPIO.OUT)
    GPIO.setup(relais7Pin, GPIO.OUT)
    GPIO.setup(relais8Pin, GPIO.OUT)
''' ---------------------------- /Raspberry PINS for Relais Switch ---------------------------- '''





''' ---------------------------- Dont change or remove these values ---------------------------- '''
'''overall values'''
time1 = '' # time decl for clock
pwmOn = 0 #value if already placed pwm page
enableOnOff = 0 #value if already placed on page 
cdOn = 0 #value if already placed on page 
currOpenedRelais = 0 # get current relais which is open for correct time for displaying on modes

# counters for all
ctrHr_Puls = 0
ctrMin_Puls = 0
ctrSec_Puls = 0

ctrHr_Pause = 0
ctrMin_Pause = 0
ctrSec_Pause = 0

ctrHr_CD = 0
ctrMin_CD = 0
ctrSec_CD = 0
'''/overall values'''

''' PWM values'''
# get information which mode is active
infoOnOff = None 
infoPWM = None
infoCD = None

PWMkill1 = threading.Event #setup vars for stopping thread
PWMkill2 = threading.Event
PWMkill3 = threading.Event
PWMkill4 = threading.Event
PWMkill5 = threading.Event
PWMkill6 = threading.Event
PWMkill7 = threading.Event
PWMkill8 = threading.Event

pwmt1 = threading.Thread #setup vars for starting thread
pwmt2 = threading.Thread
pwmt3 = threading.Thread
pwmt4 = threading.Thread
pwmt5 = threading.Thread
pwmt6 = threading.Thread
pwmt7 = threading.Thread
pwmt8 = threading.Thread
'''/PWM values'''

'''CD values'''
CDkill1 = threading.Event
CDkill2 = threading.Event
CDkill3 = threading.Event
CDkill4 = threading.Event
CDkill5 = threading.Event
CDkill6 = threading.Event
CDkill7 = threading.Event
CDkill8 = threading.Event

cdt1 = threading.Thread
cdt2 = threading.Thread
cdt3 = threading.Thread
cdt4 = threading.Thread
cdt5 = threading.Thread
cdt6 = threading.Thread
cdt7 = threading.Thread
cdt8 = threading.Thread
'''/CD values'''

'''import and export'''
countrel = { #check if activated or deactivated relais for import / export page
"rel1": 0,
"rel2": 0,
"rel3": 0,
"rel4": 0,
"rel5": 0,
"rel6": 0,
"rel7": 0,
"rel8": 0,
"relAll": 0}

selectedrel = { # translated selected relais for import / export
    "rel1": False,
    "rel2": False,
    "rel3": False,
    "rel4": False,
    "rel5": False,
    "rel6": False,
    "rel7": False,
    "rel8": False}

countImport = 0 # check if import or export
selectedcfg = 0 # check which config selected
selectedmode = False # translated selected mode for import / export

config1 = configparser.ConfigParser #preseted configs
config2 = configparser.ConfigParser
config3 = configparser.ConfigParser
config4 = configparser.ConfigParser
'''/import and export'''

'''reset page'''
count = 0 # get two functions with one button counter
'''/reset page'''
''' ---------------------------- /Dont change these values ---------------------------- '''





''' ---------------------------- Changeable settings ---------------------------- '''
fgcolor = "#42b029" # fg color for unclicked buttons
fgcolorHover = "#377e32" # fg color hover for unclicked buttons
fgcolorPressed = "#f58f00" # fg color for clicked buttons
fgcolorPressedHover = "#ffcc00" # fg color hover for clicked buttons

# paths for on windows and rpi
pathnrml = 'config.ini'
path = '/home/config.ini'

# increase fields max values
hrsMax = 80
minsMax = 59
secsMax = 59

# setting up window in tkinter
maintk = Tk()
maintk.geometry("800x480") # resolution
maintk.title("Schaltsimulator")
maintk.attributes("-fullscreen", False)
maintk.attributes('-alpha',0.85) # transparent
bg = Label(maintk, bg = "white", width = 800, height = 480) # background color
bg.place(x=0, y =0)
''' ---------------------------- /Changeable settings ---------------------------- '''