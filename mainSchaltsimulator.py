# Schaltsimulator Main script v1.0
# 
# prevent from standby 
# https://scribles.net/disabling-screen-sleep-on-raspberry-pi-2/
#
# set autostart 
# https://forums.raspberrypi.com/viewtopic.php?t=294014 | create in /etc/xdg/autostart a new .desktop file with 
    # [Desktop Entry]
    # Name=Nameofprogram
    # Exec=python3 "path to program"
    # Type=Application
#
# change rotation of rpi display
# https://www.raspberrypi-spy.co.uk/2017/11/how-to-rotate-the-raspberry-pi-display-output/
#
# von Sascha Dolgow

from tkinter import * # ui
from tkinter import messagebox # ui messagebox
from tkinter_custom_button import TkinterCustomButton # in directory
from variableDeclarations import * # all variables and definitons declared
from initUI import * # in directory for some UI and side functions
from seperateFunctions import *
import time
import threading
import configparser
import sys
import os

''' ---------------------------- Overall Functions ---------------------------- '''
def readConfig():
    '''Read main config at beginning'''
    global config
    config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    if "win" in sys.platform:
        with open(r''+pathnrml, 'r') as configFile:
            config.read_file(configFile)   
    else:
        with open(r''+path, 'r') as configFile:
            config.read_file(configFile) 


def writeConfig(section, mode, value):
    '''Write into the Config File'''
    global config
    if config.has_option(section, mode):
        config.set(section, mode, value)
        if "win" in sys.platform:
            with open(r''+pathnrml, 'w') as configFile:
                config.write(configFile)
                configFile.flush()
                os.fsync(configFile.fileno())
        else:
            with open(r''+path, 'w') as configFile:
                config.write(configFile)
                configFile.flush()
                os.fsync(configFile.fileno())

def resetWriteConfig(rel = 0, resetall = False):
    '''Reset config to Default settings'''
    global config
    my_list = [ #every variable on config
        "relais"+str(rel), 
        "relais"+str(rel)+"_mode",
        "relais"+str(rel)+"ctrhour_puls",
        "relais"+str(rel)+"ctrminute_puls",
        "relais"+str(rel)+"ctrsecond_puls", 
        "relais"+str(rel)+"ctrhour_pause",
        "relais"+str(rel)+"ctrminute_pause", 
        "relais"+str(rel)+"ctrsecond_pause", 
        "relais"+str(rel)+"ctrhour_cd",
        "relais"+str(rel)+"ctrminute_cd", 
        "relais"+str(rel)+"ctrsecond_cd",
        "relais"+str(rel)+"timecdleft", 
        "relais"+str(rel)+"modeactivepwm",
        "relais"+str(rel)+"modeactivecd"]

    if resetall == False: #reset only specific relais
        for i in my_list:
            ret = config.get("DEFAULT", i)
            config.set("SAVE", i, ret)
    else: #reset all
        for i in range(1,9): #reset every relais
            resetWriteConfig(i)

def clockTick():
    """Refresh clock timer every 200ms"""
    global time1
    time2 = time.strftime('%H:%M:%S %d/%m/%Y') # get the current local time from the PC
    if time2 != time1: # if time string has changed, update it
        time1 = time2
        clock.config(text=time2)
    # calls itself every 200 milliseconds
    clock.after(200, clockTick)

def checkModesActive():
    '''check if any mode is active'''
    allRelaisModes = []
    for i in range(1,9):
        print(i)
        allRelaisModes.append("relais"+str(i)+"modeactivepwm")
        allRelaisModes.append("relais"+str(i)+"modeactivecd")
    
    for i in range(0,16):
        if config["SAVE"][allRelaisModes[i]] == "True":
            return True
    return False

def switchButtons(btn):
    """Switch background colors of 4 modes Buttons"""
    #reset all
    btnRelaisOn.configure_color(fg_color=fgcolor)
    btnRelaisPWM.configure_color(fg_color=fgcolor)
    btnRelaisCD.configure_color(fg_color=fgcolor)
    if btn == 1: #on
        btnRelaisOn.configure_color(fg_color=fgcolorHover)
    elif btn == 2: #pwm
        btnRelaisPWM.configure_color(fg_color=fgcolorHover)
    elif btn == 3: #cd
        btnRelaisCD.configure_color(fg_color=fgcolorHover)

def switchRelaisButtons(btn):
    """Switch background colors of all 8 Relais on top"""
    btnRelais1.configure_color(fg_color=fgcolor)
    btnRelais2.configure_color(fg_color=fgcolor)
    btnRelais3.configure_color(fg_color=fgcolor)
    btnRelais4.configure_color(fg_color=fgcolor)
    btnRelais5.configure_color(fg_color=fgcolor)
    btnRelais6.configure_color(fg_color=fgcolor)
    btnRelais7.configure_color(fg_color=fgcolor)
    btnRelais8.configure_color(fg_color=fgcolor)
    if btn == 1:
        btnRelais1.configure_color(fg_color=fgcolorHover)
    elif btn == 2:
        btnRelais2.configure_color(fg_color=fgcolorHover)
    elif btn == 3:
        btnRelais3.configure_color(fg_color=fgcolorHover)
    elif btn == 4:
        btnRelais4.configure_color(fg_color=fgcolorHover)
    elif btn == 5:
        btnRelais5.configure_color(fg_color=fgcolorHover)
    elif btn == 6:
        btnRelais6.configure_color(fg_color=fgcolorHover)
    elif btn == 7:
        btnRelais7.configure_color(fg_color=fgcolorHover)
    elif btn == 8:
        btnRelais8.configure_color(fg_color=fgcolorHover)

def getRelaisGPIO(rel):
    '''get the right gpio pin from relais number'''
    if rel == 1:
        return relais1Pin
    elif rel == 2:
        return relais2Pin
    elif rel == 3:
        return relais3Pin 
    elif rel == 4:
        return relais4Pin
    elif rel == 5:
        return relais5Pin
    elif rel == 6:
        return relais6Pin
    elif rel == 7:
        return relais7Pin
    elif rel == 8:
        return relais8Pin

def checkRelaisStates():
    '''Check Active Modes on boot to restart them'''
    #datetime
    for i in range(1, 9):
        if config["SAVE"]["Relais"+str(i)] == "True": #check onoff page
            if "win" in sys.platform:
                print(i, "HIGH")
            else:
                GPIO.output(getRelaisGPIO(i), GPIO.HIGH)
        if config["SAVE"]["relais"+str(i)+"modeactivepwm"] == "True":
            writeConfig("SAVE", "relais"+str(i)+"modeactivepwm", False)
            startMode("pwm", True, i, True)
        if config["SAVE"]["relais"+str(i)+"modeactivecd"] == "True":
            writeConfig("SAVE", "relais"+str(i)+"modeactivecd", False)
            startMode("cd", True, i, True)

def addValue(mode, time, rel): # use relais var later
    """Adding values to pwm and cd modes"""
    global ctrHr_Puls
    global ctrMin_Puls
    global ctrSec_Puls

    global ctrHr_Pause
    global ctrMin_Pause
    global ctrSec_Pause

    global ctrHr_CD
    global ctrMin_CD
    global ctrSec_CD

    if mode == "pwmPuls":
        ctrHr_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrhour_puls"])
        ctrMin_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrminute_puls"])
        ctrSec_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_puls"])
        if time == "hour":
            if ctrHr_Puls < hrsMax and ctrHr_Puls >= 0:
                ctrHr_Puls += 1
            elif ctrHr_Puls == hrsMax:
                ctrHr_Puls = 0
            if ctrSec_Puls == 0 and ctrMin_Puls == 0 and ctrHr_Puls == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Puls = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_puls", str(ctrSec_Puls)) 
                lblRelaisPWM_Sec_Value_Puls.configure(text=ctrSec_Puls)

            writeConfig("SAVE", "relais"+str(rel)+"ctrhour_puls", str(ctrHr_Puls))
            lblRelaisPWM_Hour_Value_Puls.configure(text=ctrHr_Puls)
        if time == "minute":
            if ctrMin_Puls < minsMax and ctrMin_Puls >= 0:
                ctrMin_Puls += 1
            elif ctrMin_Puls == minsMax:
                ctrMin_Puls = 0
            if ctrSec_Puls == 0 and ctrMin_Puls == 0 and ctrHr_Puls == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Puls = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_puls", str(ctrSec_Puls)) 
                lblRelaisPWM_Sec_Value_Puls.configure(text=ctrSec_Puls)

            writeConfig("SAVE", "relais"+str(rel)+"ctrminute_puls", str(ctrMin_Puls))
            lblRelaisPWM_Min_Value_Puls.configure(text=ctrMin_Puls)
        if time == "second":
            if ctrSec_Puls < secsMax and ctrSec_Puls >= 0:
                ctrSec_Puls += 1
            elif ctrSec_Puls == secsMax:
                ctrSec_Puls = 0
            if ctrSec_Puls == 0 and ctrMin_Puls == 0 and ctrHr_Puls == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Puls = 1
            writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_puls", str(ctrSec_Puls))
            lblRelaisPWM_Sec_Value_Puls.configure(text=ctrSec_Puls)

    elif mode == "pwmPause":
        ctrHr_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrhour_pause"])
        ctrMin_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrminute_pause"])
        ctrSec_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_pause"])
        if time == "hour":
            if ctrHr_Pause < hrsMax and ctrHr_Pause >= 0:
                ctrHr_Pause += 1   
            elif ctrHr_Pause == hrsMax:
                ctrHr_Pause = 0
            if ctrSec_Pause == 0 and ctrMin_Pause == 0 and ctrHr_Pause == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Pause = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_pause", str(ctrSec_Pause))
                lblRelaisPWM_Sec_Value_Pause.configure(text=ctrSec_Pause)

            writeConfig("SAVE", "relais"+str(rel)+"ctrhour_pause", str(ctrHr_Pause))
            lblRelaisPWM_Hour_Value_Pause.configure(text=ctrHr_Pause)
        if time == "minute":
            if ctrMin_Pause < minsMax and ctrMin_Pause >= 0:
                ctrMin_Pause += 1  
            elif ctrMin_Pause == minsMax:
                ctrMin_Pause = 0
            if ctrSec_Pause == 0 and ctrMin_Pause == 0 and ctrHr_Pause == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Pause = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_pause", str(ctrSec_Pause))
                lblRelaisPWM_Sec_Value_Pause.configure(text=ctrSec_Pause)

            writeConfig("SAVE", "relais"+str(rel)+"ctrminute_pause", str(ctrMin_Pause))
            lblRelaisPWM_Min_Value_Pause.configure(text=ctrMin_Pause)
        if time == "second":
            if ctrSec_Pause < secsMax and ctrSec_Pause >= 0:
                ctrSec_Pause += 1  
            elif ctrSec_Pause == secsMax:
                ctrSec_Pause = 0
            if ctrSec_Pause == 0 and ctrMin_Pause == 0 and ctrHr_Pause == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Pause = 1      
            writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_pause", str(ctrSec_Pause))
            lblRelaisPWM_Sec_Value_Pause.configure(text=ctrSec_Pause)

    elif mode == "cd":
        ctrHr_CD = int(config["SAVE"]["relais"+str(rel)+"ctrhour_cd"])
        ctrMin_CD = int(config["SAVE"]["relais"+str(rel)+"ctrminute_cd"])
        ctrSec_CD = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_cd"])
        if time == "hour":
            if ctrHr_CD < hrsMax and ctrHr_CD >= 0:
                ctrHr_CD += 1
            elif ctrHr_CD == hrsMax:
                ctrHr_CD = 0
            if ctrSec_CD == 0 and ctrMin_CD == 0 and ctrHr_CD == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_CD = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_cd", str(ctrSec_CD))
                lblRelaisCD_Sec_Value.configure(text=ctrSec_CD)

            writeConfig("SAVE", "relais"+str(rel)+"ctrhour_cd", str(ctrHr_CD))
            lblRelaisCD_Hour_Value.configure(text=ctrHr_CD)
        if time == "minute":
            if ctrMin_CD < minsMax and ctrMin_CD >= 0:
                ctrMin_CD += 1
            elif ctrMin_CD == minsMax:
                ctrMin_CD = 0
            if ctrSec_CD == 0 and ctrMin_CD == 0 and ctrHr_CD == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_CD = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_cd", str(ctrSec_CD))
                lblRelaisCD_Sec_Value.configure(text=ctrSec_CD)

            writeConfig("SAVE", "relais"+str(rel)+"ctrminute_cd", str(ctrMin_CD))
            lblRelaisCD_Min_Value.configure(text=ctrMin_CD)
        if time == "second":
            if ctrSec_CD < secsMax and ctrSec_CD >= 0:
                ctrSec_CD += 1
            elif ctrSec_CD == secsMax:
                ctrSec_CD = 0
            if ctrSec_CD == 0 and ctrMin_CD == 0 and ctrHr_CD == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_CD = 1
            writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_cd", str(ctrSec_CD))
            lblRelaisCD_Sec_Value.configure(text=ctrSec_CD)
        lblRelaisCD_CD.configure(text=calcNullPosition(ctrHr_CD,ctrMin_CD,ctrSec_CD))

def decValue(mode, time, rel):
    """Adding values to pwm and cd modes"""
    global ctrHr_Puls
    global ctrMin_Puls
    global ctrSec_Puls

    global ctrHr_Pause
    global ctrMin_Pause
    global ctrSec_Pause

    global ctrHr_CD
    global ctrMin_CD
    global ctrSec_CD

    if mode == "pwmPuls":
        ctrHr_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrhour_puls"])
        ctrMin_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrminute_puls"])
        ctrSec_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_puls"])
        if time == "hour":
            if ctrHr_Puls <= hrsMax and ctrHr_Puls >= 1:
                ctrHr_Puls -= 1
            elif ctrHr_Puls == 0:
                ctrHr_Puls = hrsMax
            if ctrSec_Puls == 0 and ctrMin_Puls == 0 and ctrHr_Puls == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Puls = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_puls", str(ctrSec_Puls)) 
                lblRelaisPWM_Sec_Value_Puls.configure(text=ctrSec_Puls)

            writeConfig("SAVE", "relais"+str(rel)+"ctrhour_puls", str(ctrHr_Puls))
            lblRelaisPWM_Hour_Value_Puls.configure(text=ctrHr_Puls)
        if time == "minute":
            if ctrMin_Puls <= minsMax and ctrMin_Puls >= 1:
                ctrMin_Puls -= 1    
            elif ctrMin_Puls == 0:
                ctrMin_Puls = minsMax   
            if ctrSec_Puls == 0 and ctrMin_Puls == 0 and ctrHr_Puls == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Puls = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_puls", str(ctrSec_Puls)) 
                lblRelaisPWM_Sec_Value_Puls.configure(text=ctrSec_Puls)

            writeConfig("SAVE", "relais"+str(rel)+"ctrminute_puls", str(ctrMin_Puls))
            lblRelaisPWM_Min_Value_Puls.configure(text=ctrMin_Puls)
        if time == "second":
            if ctrSec_Puls <= secsMax and ctrSec_Puls >= 1:
                ctrSec_Puls -= 1  
            elif ctrSec_Puls == 0:
                ctrSec_Puls = secsMax   
            if ctrSec_Puls == 0 and ctrMin_Puls == 0 and ctrHr_Puls == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Puls = secsMax
            writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_puls", str(ctrSec_Puls)) 
            lblRelaisPWM_Sec_Value_Puls.configure(text=ctrSec_Puls)

    elif mode == "pwmPause":
        ctrHr_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrhour_pause"])
        ctrMin_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrminute_pause"])
        ctrSec_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_pause"])
        if time == "hour":
            if ctrHr_Pause <= hrsMax and ctrHr_Pause >= 1:
                ctrHr_Pause -= 1    
            elif ctrHr_Pause == 0:
                ctrHr_Pause = hrsMax
            if ctrSec_Pause == 0 and ctrMin_Pause == 0 and ctrHr_Pause == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Pause = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_pause", str(ctrSec_Pause))
                lblRelaisPWM_Sec_Value_Pause.configure(text=ctrSec_Pause)

            writeConfig("SAVE", "relais"+str(rel)+"ctrhour_pause", str(ctrHr_Pause))
            lblRelaisPWM_Hour_Value_Pause.configure(text=ctrHr_Pause)
        if time == "minute":
            if ctrMin_Pause <= minsMax and ctrMin_Pause >= 1:
                ctrMin_Pause -= 1
            elif ctrMin_Pause == 0:
                ctrMin_Pause = minsMax    
            if ctrSec_Pause == 0 and ctrMin_Pause == 0 and ctrHr_Pause == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Pause = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_pause", str(ctrSec_Pause))
                lblRelaisPWM_Sec_Value_Pause.configure(text=ctrSec_Pause)

            writeConfig("SAVE", "relais"+str(rel)+"ctrminute_pause", str(ctrMin_Pause))
            lblRelaisPWM_Min_Value_Pause.configure(text=ctrMin_Pause)
        if time == "second":
            if ctrSec_Pause <= secsMax and ctrSec_Pause >= 1:
                ctrSec_Pause -= 1    
            elif ctrSec_Pause == 0:
                ctrSec_Pause = secsMax
            if ctrSec_Pause == 0 and ctrMin_Pause == 0 and ctrHr_Pause == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_Pause = secsMax
            writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_pause", str(ctrSec_Pause))
            lblRelaisPWM_Sec_Value_Pause.configure(text=ctrSec_Pause)

    elif mode == "cd":
        ctrHr_CD = int(config["SAVE"]["relais"+str(rel)+"ctrhour_cd"])
        ctrMin_CD = int(config["SAVE"]["relais"+str(rel)+"ctrminute_cd"])
        ctrSec_CD = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_cd"])
        if time == "hour":
            if ctrHr_CD <= hrsMax and ctrHr_CD >= 1:
                ctrHr_CD -= 1
            elif ctrHr_CD == 0:
                ctrHr_CD = hrsMax
            if ctrSec_CD == 0 and ctrMin_CD == 0 and ctrHr_CD == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_CD = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_cd", str(ctrSec_CD))
                lblRelaisCD_Sec_Value.configure(text=ctrSec_CD)

            writeConfig("SAVE", "relais"+str(rel)+"ctrhour_cd", str(ctrHr_CD))
            lblRelaisCD_Hour_Value.configure(text=ctrHr_CD)
        if time == "minute":
            if ctrMin_CD <= minsMax and ctrMin_CD >= 1:
                ctrMin_CD -= 1
            elif ctrMin_CD == 0:
                ctrMin_CD = minsMax
            if ctrSec_CD == 0 and ctrMin_CD == 0 and ctrHr_CD == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_CD = 1
                writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_cd", str(ctrSec_CD))
                lblRelaisCD_Sec_Value.configure(text=ctrSec_CD)

            writeConfig("SAVE", "relais"+str(rel)+"ctrminute_cd", str(ctrMin_CD))
            lblRelaisCD_Min_Value.configure(text=ctrMin_CD)
        if time == "second":
            if ctrSec_CD <= secsMax and ctrSec_CD >= 1:
                ctrSec_CD -= 1
            elif ctrSec_CD == 0:
                ctrSec_CD = secsMax
            if ctrSec_CD == 0 and ctrMin_CD == 0 and ctrHr_CD == 0: #dont let 0 | 0 | 0 pickable
                ctrSec_CD = secsMax
            writeConfig("SAVE", "relais"+str(rel)+"ctrsecond_cd", str(ctrSec_CD))
            lblRelaisCD_Sec_Value.configure(text=ctrSec_CD)

        lblRelaisCD_CD.configure(text=calcNullPosition(ctrHr_CD,ctrMin_CD,ctrSec_CD))
''' ---------------------------- /Overall functions ---------------------------- '''





''' ---------------------------- Start Page ---------------------------- '''
def initHeadButtons(master): #init all buttons on start /init.py
    """Initialize all head Buttons of Window"""
    #TOP RELAIS start and change colors
    global btnRelais1
    global btnRelais2
    global btnRelais3
    global btnRelais4
    global btnRelais5
    global btnRelais6
    global btnRelais7
    global btnRelais8

    global btnreset
    btnreset = addButtons(master, "Settings", 700, 0, h=32.5,fgC="#DADADA", hovC="#929292" ,cmdFunc=resetPage)
    frame = Frame(maintk, width = 800, height = 5, highlightbackground="#47464c", highlightcolor="#47464c",background="#47464c" , highlightthickness=1)
    frame.place(x = 0, y = 97.5)
    
    btnRelais1 = addButtons(master, "Relais 1",0,32.5, cmdFunc=lambda: relaisPage(1))
    btnRelais2 = addButtons(master, "Relais 2",100,32.5,cmdFunc=lambda: relaisPage(2))
    btnRelais3 = addButtons(master, "Relais 3",200,32.5, cmdFunc=lambda: relaisPage(3))
    btnRelais4 = addButtons(master, "Relais 4",300,32.5, cmdFunc=lambda: relaisPage(4))
    btnRelais5 = addButtons(master, "Relais 5",400,32.5, cmdFunc=lambda: relaisPage(5))
    btnRelais6 = addButtons(master, "Relais 6",500,32.5, cmdFunc=lambda: relaisPage(6))
    btnRelais7 = addButtons(master, "Relais 7",600,32.5, cmdFunc=lambda: relaisPage(7))
    btnRelais8 = addButtons(master, "Relais 8",700,32.5, cmdFunc=lambda: relaisPage(8))

def initTitle(master):
    """Initialze title text and logo"""
    addLabelPlace(master, "Title", "Schaltsimulator", xPos=0, yPos=7, fontSize=15)
    addLabelPack(master, "lblcopyright",text="r2p 2021-"+ time.strftime('%Y'), fontSize=15, anchor=SE, side=BOTTOM)

flag = 0
def relaisPage(rel):
    """Main Window for Relais"""
    global flag
    if flag != rel: # only let open once
        flag = rel
        # before changing relais reset all unsaved settings
        deleteOnOffPage()
        deletePWMPage()
        deleteCDPage()

        global btnRelaisOn
        global btnRelaisOff
        global btnRelaisPWM
        global btnRelaisCD


        global currOpenedRelais
        currOpenedRelais = rel
        switchRelaisButtons(rel) # switch background colors of relais for loc

        frameBox = Frame(maintk, width = 600, height = 320, highlightbackground="black", highlightcolor="black",background="white" , highlightthickness=1)
        frameBox.place(x = 100, y = 131)

        frameBoxLine = Frame(maintk, width = 600, height = 5, highlightbackground="#47464c", highlightcolor="#47464c",background="#47464c" , highlightthickness=1)
        frameBoxLine.place(x = 100, y = 196)

        btnRelaisOn = addButtons(maintk, "Ein- und Ausschalten", xPos=100, yPos=131,w=200, cmdFunc=lambda: relaisOnOffPage(rel))
        btnRelaisPWM = addButtons(maintk, "PWM", xPos=300, yPos=131, w=200, cmdFunc=lambda: relaisPWM(rel))
        btnRelaisCD = addButtons(maintk, "Countdown", xPos=500, yPos=131, w=200, cmdFunc=lambda: relaisCD(rel))

        global infoOnOff
        global infoPWM
        global infoCD
        infoOnOff = btnRelaisOn.place_info()
        infoPWM = btnRelaisPWM.place_info()
        infoCD = btnRelaisCD.place_info()
        if config["SAVE"]["Relais"+str(rel)+"_mode"] == "OnOff":
            relaisOnOffPage(rel)
        elif config["SAVE"]["Relais"+str(rel)+"_mode"] == "PWM":
            relaisPWM(rel)
            btnRelaisOn.place_forget()
            btnRelaisCD.place_forget()
        elif config["SAVE"]["Relais"+str(rel)+"_mode"] == "CD":
            relaisCD(rel)
            btnRelaisOn.place_forget()
            btnRelaisPWM.place_forget()

def startMode(mode, OnOffState, rel, onboot = False):
    ''''Starting PWM and CD modes'''
    global infoOnOff
    global infoPWM
    global infoCD
    if mode == "pwm": # starts pwm
        if config["SAVE"]["Relais"+str(rel)+"_mode"] != "PWM":
                writeConfig("SAVE", "Relais"+str(rel)+"_mode", "PWM")
        if OnOffState == True and not config["SAVE"]["relais"+str(rel)+"modeactivepwm"] == "True": #check if modeactive, so can only press once
            print("starts")
            if onboot == False:
                btnRelaisPWM_Start.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            writeConfig("SAVE", "Relais"+str(rel)+"modeactivepwm", "True")
            global ctrHr_Puls
            global ctrMin_Puls
            global ctrSec_Puls

            global ctrHr_Pause
            global ctrMin_Pause
            global ctrSec_Pause
            if onboot == False:
                btnRelaisOn.place_forget()
                btnRelaisCD.place_forget()

            if ctrHr_Puls or ctrMin_Puls or ctrSec_Puls or ctrHr_Pause or ctrMin_Pause or ctrSec_Pause<= 0: # if values are all 0, check again values from config
                ctrHr_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrhour_puls"])
                ctrMin_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrminute_puls"])
                ctrSec_Puls = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_puls"])

                ctrHr_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrhour_pause"])
                ctrMin_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrminute_pause"])
                ctrSec_Pause = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_pause"])
            
            refvalPuls = (ctrHr_Puls*60*60)+(ctrMin_Puls*60)+(ctrSec_Puls)
            refvalPause = (ctrHr_Pause*60*60)+(ctrMin_Pause*60)+(ctrSec_Pause)

            print("PULS: ", refvalPuls)
            print("PAUSE: ", refvalPause)
            global PWMkill1
            global PWMkill2
            global PWMkill3
            global PWMkill4
            global PWMkill5
            global PWMkill6
            global PWMkill7
            global PWMkill8

            global pwmt1
            global pwmt2
            global pwmt3
            global pwmt4
            global pwmt5
            global pwmt6
            global pwmt7
            global pwmt8

            if rel == 1:
                PWMkill1 = threading.Event()
                pwmt1 = threading.Thread(target=pwmTimer, args=(PWMkill1, "task", rel, refvalPuls, refvalPause))
                pwmt1.start()
            elif rel == 2:
                PWMkill2 = threading.Event()
                pwmt2 = threading.Thread(target=pwmTimer, args=(PWMkill2, "task", rel, refvalPuls, refvalPause))
                pwmt2.start()
            elif rel == 3:
                PWMkill3 = threading.Event()
                pwmt3 = threading.Thread(target=pwmTimer, args=(PWMkill3, "task", rel, refvalPuls, refvalPause))
                pwmt3.start()
            elif rel == 4:
                PWMkill4 = threading.Event()
                pwmt4 = threading.Thread(target=pwmTimer, args=(PWMkill4, "task", rel, refvalPuls, refvalPause))
                pwmt4.start()
            elif rel == 5:
                PWMkill5 = threading.Event()
                pwmt5 = threading.Thread(target=pwmTimer, args=(PWMkill5, "task", rel, refvalPuls, refvalPause))
                pwmt5.start()
            elif rel == 6:
                PWMkill6 = threading.Event()
                pwmt6 = threading.Thread(target=pwmTimer, args=(PWMkill6, "task", rel, refvalPuls, refvalPause))
                pwmt6.start()
            elif rel == 7:
                PWMkill7 = threading.Event()
                pwmt7 = threading.Thread(target=pwmTimer, args=(PWMkill7, "task", rel, refvalPuls, refvalPause))
                pwmt7.start()
            elif rel == 8:
                PWMkill8 = threading.Event()
                pwmt8 = threading.Thread(target=pwmTimer, args=(PWMkill8, "task", rel, refvalPuls, refvalPause))
                pwmt8.start()    

            writeConfig("SAVE", "relais"+str(rel)+"modeactivepwm", "True")
           
        elif OnOffState == False and not config["SAVE"]["relais"+str(rel)+"modeactivepwm"] == "False":
            writeConfig("SAVE", "Relais"+str(rel)+"_mode", "OnOff")
            writeConfig("SAVE", "Relais"+str(rel)+"ModeActivePWM", "False")
            # STOP TIMER THREADING HERE -----------------------------------------------------------------
            if onboot == False:
                btnRelaisOn.place(infoOnOff)
                btnRelaisCD.place(infoCD)
                btnRelaisPWM_Start.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
            print("Stops")
            if rel == 1:
                PWMkill1.set()
                pwmt1.join()
            elif rel == 2:
                PWMkill2.set()
                pwmt2.join()
            elif rel == 3:
                PWMkill3.set()
                pwmt3.join()
            elif rel == 4:
                PWMkill4.set()
                pwmt4.join()
            elif rel == 5:
                PWMkill5.set()
                pwmt5.join()
            elif rel == 6:
                PWMkill6.set()
                pwmt6.join()
            elif rel == 7:
                PWMkill7.set()
                pwmt7.join()
            elif rel == 8:
                PWMkill8.set()
                pwmt8.join()

            writeConfig("SAVE", "relais"+str(rel)+"modeactivepwm", "False")
    if mode == "cd":
        if config["SAVE"]["Relais"+str(rel)+"_mode"] != "CD":
            writeConfig("SAVE", "Relais"+str(rel)+"_mode", "CD")

        if OnOffState == True and not config["SAVE"]["relais"+str(rel)+"modeactivecd"] == "True":
            if onboot == False:
                btnRelaisCD_Start.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            writeConfig("SAVE", "Relais"+str(rel)+"modeactivecd", "True")
            if onboot == False:
                btnRelaisOn.place_forget()
                btnRelaisPWM.place_forget()
            print("Start")
            if onboot == False:
                global refsec
                global refmin
                global refhr
                refsec = int(config["SAVE"]["relais"+str(rel)+"ctrsecond_cd"])
                refmin = int(config["SAVE"]["relais"+str(rel)+"ctrminute_cd"])
                refhr = int(config["SAVE"]["relais"+str(rel)+"ctrhour_cd"])
                refsum = (refhr*60*60)+(refmin*60)+refsec
                print(refsum)
            elif onboot == True:
                refsum = int(config["SAVE"]["relais"+str(rel)+"timecdleft"])

            global CDkill1
            global CDkill2
            global CDkill3
            global CDkill4
            global CDkill5
            global CDkill6
            global CDkill7
            global CDkill8

            global cdt1
            global cdt2
            global cdt3
            global cdt4
            global cdt5
            global cdt6
            global cdt7
            global cdt8
            if rel == 1:
                CDkill1 = threading.Event()
                cdt1 = threading.Thread(target=cdTimer, args=(CDkill1, "task", rel, refsum))
                cdt1.start()
            if rel == 2:
                CDkill2 = threading.Event()
                cdt2 = threading.Thread(target=cdTimer, args=(CDkill2, "task", rel, refsum))
                cdt2.start()
            if rel == 3:
                CDkill3 = threading.Event()
                cdt3 = threading.Thread(target=cdTimer, args=(CDkill3, "task", rel, refsum))
                cdt3.start()
            if rel == 4:
                CDkill4 = threading.Event()
                cdt4 = threading.Thread(target=cdTimer, args=(CDkill4, "task", rel, refsum))
                cdt4.start()
            if rel == 5:
                CDkill5 = threading.Event()
                cdt5 = threading.Thread(target=cdTimer, args=(CDkill5, "task", rel, refsum))
                cdt5.start()
            if rel == 6:
                CDkill6 = threading.Event()
                cdt6 = threading.Thread(target=cdTimer, args=(CDkill6, "task", rel, refsum))
                cdt6.start()
            if rel == 7:
                CDkill7 = threading.Event()
                cdt7 = threading.Thread(target=cdTimer, args=(CDkill7, "task", rel, refsum))
                cdt7.start()
            if rel == 8:
                CDkill8 = threading.Event()
                cdt8 = threading.Thread(target=cdTimer, args=(CDkill8, "task", rel, refsum))
                cdt8.start()

            writeConfig("SAVE", "relais"+str(rel)+"modeactivecd", "True")
        elif OnOffState == False and not config["SAVE"]["relais"+str(rel)+"modeactivecd"] == "False":
            print("stopping")
            if onboot == False:
                btnRelaisCD_Start.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
                btnRelaisOn.place(infoOnOff)
                btnRelaisPWM.place(infoPWM)

            if rel == 1:
                CDkill1.set()
                cdt1.join()
            elif rel == 2:
                CDkill2.set()
                cdt2.join()
            elif rel == 3:
                CDkill3.set()
                cdt3.join()
            elif rel == 4:
                CDkill4.set()
                cdt4.join()
            elif rel == 5:
                CDkill5.set()
                cdt5.join()
            elif rel == 6:
                CDkill6.set()
                cdt6.join()
            elif rel == 7:
                CDkill7.set()
                cdt7.join()
            elif rel == 8:
                CDkill8.set()
                cdt8.join()

            reftimeleft = int(config["SAVE"]["relais"+str(rel)+"timecdleft"])
            if reftimeleft <= 0:
                refreshCDRelais(rel)
            writeConfig("SAVE","relais"+str(rel)+"timecdleft", "0") # reset timer value
            writeConfig("SAVE", "relais"+str(rel)+"modeactivecd", "False")
            writeConfig("SAVE", "Relais"+str(rel)+"_mode", "OnOff")
''' ---------------------------- /Start Page ---------------------------- '''





''' ---------------------------- Reset page ---------------------------- '''
def resetPage():
    '''build reset page or unbuild it'''
    global count
    if count%2 == 0: #reset page
        deleteOnOffPage()
        deleteCDPage()
        deletePWMPage()
        btnRelaisOn.place_forget()
        btnRelaisPWM.place_forget()
        btnRelaisCD.place_forget()

        global frameResetInfo
        global lblResetInfo
        global frameResetWindow

        global btnResetRelais1
        global btnResetRelais2
        global btnResetRelais3
        global btnResetRelais4
        global btnResetRelais5
        global btnResetRelais6
        global btnResetRelais7
        global btnResetRelais8
        global btnResetRelaisAll

        global btnimport
        btnimport = addButtons(maintk, "Import/Export", 600, 0, h=32.5,fgC="#DADADA", hovC="#929292" ,cmdFunc=importPage)

        btnreset.set_text("Zurück")
        frameResetInfo = Frame(maintk, width = 600, height = 65, highlightbackground=fgcolor, highlightcolor=fgcolor,background=fgcolor , highlightthickness=1)
        frameResetInfo.place(x = 100, y = 131)
        lblResetInfo = addLabelPlace(maintk,"lblresetinfo", "Zum Zurücksetzen die Relais-Felder anklicken oder unten alle Relais Zurücksetzen.", 142.5, 155, bg=fgcolor, fontSize=10)
        frameResetWindow = Frame(maintk, width = 800, height = 65, highlightbackground=fgcolor, highlightcolor=fgcolor,background=fgcolor , highlightthickness=1)
        frameResetWindow.place(x = 0, y = 32.5)

        btnResetRelais1 = addButtons(maintk, "Relais 1",212.5,230, w=75, h=49, cmdFunc=lambda: resetWindow(1))
        btnResetRelais2 = addButtons(maintk, "Relais 2",312.5,230, w=75, h=49, cmdFunc=lambda: resetWindow(2))
        btnResetRelais3 = addButtons(maintk, "Relais 3",412.5,230, w=75, h=49, cmdFunc=lambda: resetWindow(3))
        btnResetRelais4 = addButtons(maintk, "Relais 4",512.5,230, w=75, h=49, cmdFunc=lambda: resetWindow(4))
        btnResetRelais5 = addButtons(maintk, "Relais 5",212.5,320, w=75, h=49, cmdFunc=lambda: resetWindow(5))
        btnResetRelais6 = addButtons(maintk, "Relais 6",312.5,320, w=75, h=49, cmdFunc=lambda: resetWindow(6))
        btnResetRelais7 = addButtons(maintk, "Relais 7",412.5,320, w=75, h=49, cmdFunc=lambda: resetWindow(7))
        btnResetRelais8 = addButtons(maintk, "Relais 8",512.5,320, w=75, h=49, cmdFunc=lambda: resetWindow(8))
        btnResetRelaisAll = addButtons(maintk, "Alle Zurücksetzen",312.5,392, w=175, h=49, cmdFunc=lambda: resetWindow(resetall=True))
    else: #unreset page / standard page
        btnreset.set_text("Settings")
        deleteResetPage() # delete page
        try:
            if btnimpexpRelais1.winfo_exists() == True: #if gone to settings and leaving dont deleteimportpage
                deleteimportPage()
        except NameError:
            pass
        global flag
        flag = 0
        relaisPage(1) # start at relais 1
    count+=1


def resetWindow(rel = 0, resetall = False):
    '''reset popup Window'''
    if resetall is True:
        MsgBox = messagebox.askquestion("Warnung","Sind Sie sicher, dass Sie alle Relais zurückgesetzen wollen?",icon = "warning")
    else:
        MsgBox = messagebox.askquestion("Warnung","Sind Sie sicher, dass Sie Relais "+str(rel)+" zurückgesetzen wollen?",icon = "warning")

    if MsgBox == "yes":
        if resetall is True: #translate to resetwriteconfig resetall = true
            if checkModesActive() == False:
                resetWriteConfig(resetall= True)
                messagebox.showinfo("Erfolgreich","Alle Relais wurden erfolgreich zurückgesetzt!")
            else:
                messagebox.showinfo("Fehler","Die Relais konnten nicht zurückgesetzt werden.\n Schalten Sie alle aktiven Timer aus!")
        else:
            if config["SAVE"]["relais"+str(rel)+"modeactivepwm"] == "False" and config["SAVE"]["relais"+str(rel)+"modeactivecd"] == "False":
                resetWriteConfig(rel) #translate relais number to resetwriteconfig
                messagebox.showinfo("Erfolgreich","Relais "+str(rel)+" wurde erfolgreich zurückgesetzt!")
            else:
                messagebox.showinfo("Fehler","Relais "+str(rel)+" konnte nicht zurückgesetzt werden.\n Schalten Sie alle aktiven Timer aus!")

def deleteResetPage(importval = False):
    '''Reset Page elements are deleting'''
    #reset page here
    if importval == False:
        frameResetInfo.place_forget()
        lblResetInfo.place_forget()
        frameResetWindow.place_forget()
    btnimport.place_forget()
    btnResetRelais1.place_forget()
    btnResetRelais2.place_forget()
    btnResetRelais3.place_forget()
    btnResetRelais4.place_forget()
    btnResetRelais5.place_forget()
    btnResetRelais6.place_forget()
    btnResetRelais7.place_forget()
    btnResetRelais8.place_forget()
    btnResetRelaisAll.place_forget()
''' ---------------------------- /Reset Page ---------------------------- '''

''' ---------------------------- Import and Export Page ---------------------------- '''
def importPage():
    deleteResetPage(True)
    lblResetInfo.configure(text="Zum Importieren oder Exportieren eine Config und die jeweiligen Relais auswählen")

    global btnImpExp

    global config1Readable
    global config1Name

    global config2Readable
    global config2Name

    global config3Readable
    global config3Name

    global config4Readable
    global config4Name

    global btncfg1
    global btncfg2
    global btncfg3
    global btncfg4

    global btnimpexpRelais1
    global btnimpexpRelais2
    global btnimpexpRelais3
    global btnimpexpRelais4
    global btnimpexpRelais5
    global btnimpexpRelais6

    global btnimpexpRelais7
    global btnimpexpRelais8
    global btnimpexpRelaisAll
    global btnimpexpStart


    btnImpExp = addButtons(maintk, "Export",162.5,230, w=75, h=49, fgC=fgcolorPressed,hovC=fgcolorPressedHover,cmdFunc=lambda: insertImportValues(impexp = True))

    config1Readable = readConfigsImportExport(config1, "config1")
    config1Name = config1Readable.get("SAVE", "configname")

    config2Readable = readConfigsImportExport(config2, "config2")
    config2Name = config2Readable.get("SAVE", "configname")

    config3Readable = readConfigsImportExport(config3, "config3")
    config3Name = config3Readable.get("SAVE", "configname")

    config4Readable = readConfigsImportExport(config4, "config4")
    config4Name = config4Readable.get("SAVE", "configname")

    btncfg1 = addButtons(maintk, config1Name,262.5,230, w=75, h=49, cmdFunc=lambda: insertImportValues(cfg=True, val=1))
    btncfg2 = addButtons(maintk, config2Name,362.5,230, w=75, h=49, cmdFunc=lambda: insertImportValues(cfg=True, val=2))
    btncfg3 = addButtons(maintk, config3Name,462.5,230, w=75, h=49, cmdFunc=lambda: insertImportValues(cfg=True, val=3))
    btncfg4 = addButtons(maintk, config4Name,562.5,230, w=75, h=49, cmdFunc=lambda: insertImportValues(cfg=True, val=4))

    btnimpexpRelais1 = addButtons(maintk, "Relais 1",112.5,320, w=75, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=1))
    btnimpexpRelais2 = addButtons(maintk, "Relais 2",212.5,320, w=75, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=2))
    btnimpexpRelais3 = addButtons(maintk, "Relais 3",312.5,320, w=75, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=3))
    btnimpexpRelais4 = addButtons(maintk, "Relais 4",412.5,320, w=75, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=4))
    btnimpexpRelais5 = addButtons(maintk, "Relais 5",512.5,320, w=75, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=5))
    btnimpexpRelais6 = addButtons(maintk, "Relais 6",612.5,320, w=75, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=6))

    btnimpexpRelais7 = addButtons(maintk, "Relais 7",112.5,392, w=75, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=7))
    btnimpexpRelais8 = addButtons(maintk, "Relais 8",212.5,392, w=75, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=8))
    btnimpexpRelaisAll = addButtons(maintk, "Alle Auswählen",312.5,392, w=175, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=9))
    btnimpexpStart = addButtons(maintk, "Start",512.5,392, w=175, h=49, cmdFunc=startImport)


def importConfig(readConfig, selRel):
    '''import config file'''
    ctr = 1
    for i in selRel:
        if selRel[i] == True:
            newList = configvalues(ctr)
            for j in newList:
                ret = readConfig.get("SAVE", j)
                config.set("SAVE", j, ret)
        ctr += 1
        if "win" in sys.platform:
            with open(r''+pathnrml, 'w') as configFile:
                config.write(configFile)
        else:
            with open(r''+path, 'w') as configFile:
                config.write(configFile)

def exportConfig(writeConfig, selRel, val):
    '''export config file'''
    ctr = 1
    for i in selRel:
        if selRel[i] == True:
            newList = configvalues(ctr)
            for j in newList:
                ret = config.get("SAVE", j)
                writeConfig.set("SAVE", j, ret)
        ctr += 1
        writeConfigs(writeConfig, "config"+str(val))

def startImport():
    '''start import button function'''
    # check before continue
    if selectedcfg == 0 or checkSelectedRelais(selectedrel) == False:
        messagebox.showinfo("Fehler","Wählen Sie alle notwendigen Felder aus!")
        return
    elif checkModesActive() == True:
        messagebox.showinfo("Fehler","Schalten Sie alle aktiven Timer aus!")
        return
    #/ check before continue
    # get selected name of config
    if selectedcfg == 1:
        configLocalName = config1Name
    elif selectedcfg == 2:
        configLocalName = config2Name
    elif selectedcfg == 3:
        configLocalName = config3Name
    elif selectedcfg == 4:
        configLocalName = config4Name
    #/ get selected name of config

    if selectedmode == True: # import
        MsgBox = messagebox.askquestion("Warnung","Sind Sie sicher, dass Sie die ausgewählten Relais in die config "+configLocalName+" importieren wollen?",icon = "warning")
        if MsgBox == "yes":
            print("main import funct")
            if selectedcfg == 1:
                importConfig(config1Readable, selectedrel)
            elif selectedcfg == 2:
                importConfig(config2Readable, selectedrel)
            elif selectedcfg == 3:
                importConfig(config3Readable, selectedrel)
            elif selectedcfg == 4:
                importConfig(config4Readable, selectedrel)

            messagebox.showinfo("Erfolgreich","Alle ausgewählten Relais wurden von "+configLocalName+" importiert!")
    elif selectedmode == False: # export
        MsgBox = messagebox.askquestion("Warnung","Sind Sie sicher, dass Sie die ausgewählten Relais in die config "+configLocalName+" exportieren wollen?",icon = "warning")
        if MsgBox == "yes":
            print("main export funct")
            if selectedcfg == 1:
                exportConfig(config1Readable, selectedrel, selectedcfg)
            elif selectedcfg == 2:
                exportConfig(config2Readable, selectedrel, selectedcfg)
            elif selectedcfg == 3:
                exportConfig(config3Readable, selectedrel, selectedcfg)
            elif selectedcfg == 4:
                exportConfig(config4Readable, selectedrel, selectedcfg)
            messagebox.showinfo("Erfolgreich","Alle ausgewählten Relais wurden von "+configLocalName+" exportiert!")

def setImportColors(cfg = False, rel = False, val = 0, state = False):
    '''set or unset import / export colors for buttons'''
    if cfg == True:
        btncfg1.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        btncfg2.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        btncfg3.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        btncfg4.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        if val == 1:
            btncfg1.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
        elif val == 2:
            btncfg2.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
        elif val == 3:
            btncfg3.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
        elif val == 4:
            btncfg4.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
    if rel == True:
        if val == 1:
            if state:
                btnimpexpRelais1.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais1.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        elif val == 2:
            if state:
                btnimpexpRelais2.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais2.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        elif val == 3:
            if state:
                btnimpexpRelais3.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais3.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        elif val == 4:
            if state:
                btnimpexpRelais4.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais4.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        elif val == 5:
            if state:
                btnimpexpRelais5.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais5.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        elif val == 6:
            if state:
                btnimpexpRelais6.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais6.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        elif val == 7:
            if state:
                btnimpexpRelais7.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais7.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        elif val == 8:
            if state:
                btnimpexpRelais8.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais8.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        elif val == 9:
            if state:
                global btnimpexpRelaisAll

                btnimpexpRelais1.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
                btnimpexpRelais2.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
                btnimpexpRelais3.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
                btnimpexpRelais4.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
                btnimpexpRelais5.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
                btnimpexpRelais6.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
                btnimpexpRelais7.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
                btnimpexpRelais8.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)

                btnimpexpRelaisAll.place_forget()
                btnimpexpRelaisAll = addButtons(maintk, "Alle Abwählen",312.5,392, w=175, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=9))
                btnimpexpRelaisAll.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            else:
                btnimpexpRelais1.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
                btnimpexpRelais2.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
                btnimpexpRelais3.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
                btnimpexpRelais4.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
                btnimpexpRelais5.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
                btnimpexpRelais6.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
                btnimpexpRelais7.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
                btnimpexpRelais8.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)

                btnimpexpRelaisAll.place_forget()
                btnimpexpRelaisAll = addButtons(maintk, "Alle Auswählen",312.5,392, w=175, h=49, cmdFunc=lambda: insertImportValues(rel=True, val=9))
                btnimpexpRelaisAll.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)

def deleteimportPage():
    '''delete import / export page'''
    btnimpexpRelais1.place_forget()
    btnimpexpRelais2.place_forget()
    btnimpexpRelais3.place_forget()
    btnimpexpRelais4.place_forget()
    btnimpexpRelais5.place_forget()
    btnimpexpRelais6.place_forget()
    btnimpexpRelais7.place_forget()
    btnimpexpRelais8.place_forget()
    btnimpexpRelaisAll.place_forget()
    btnimpexpStart.place_forget()
    btnImpExp.place_forget()
    
    btncfg1.place_forget()
    btncfg2.place_forget()
    btncfg3.place_forget()
    btncfg4.place_forget()

    global countImport
    global selectedcfg

    global selectedmode

    global countrel
    global selectedrel
    
    countImport = 0
    selectedcfg = 0

    selectedmode = False

    for i in countrel:
        countrel[i] = 0
    for i in selectedrel:
        selectedrel[i] = False

def insertImportValues(impexp = False, cfg = False, rel = False, val = 0):
    '''get import / export values and pass them on'''
    global countImport
    if impexp == True:
        global selectedmode
        if countImport%2 == 0:
            print("Import")
            btnImpExp.set_text("Import")
            selectedmode = True
        else:
            print("Export")
            btnImpExp.set_text("Export")
            selectedmode = False
        countImport +=1
    elif cfg == True:
        global selectedcfg
        if val == 1 and not selectedcfg == 1:
            print("1")
            setImportColors(cfg=True, val=1)
            selectedcfg = 1
        elif val == 2 and not selectedcfg == 2:
            print("2")
            setImportColors(cfg=True, val=2)
            selectedcfg = 2
        elif val == 3 and not selectedcfg == 3:
            print("3")
            setImportColors(cfg=True, val=3)
            selectedcfg = 3
        elif val == 4 and not selectedcfg == 4:
            print("4")
            setImportColors(cfg=True, val=4)
            selectedcfg = 4
    elif rel == True:
        global selectedrel
        global countrel
        if val == 1:
            if countrel["rel1"]%2 == 0:
                print("1 True")
                setImportColors(rel=True, val=1, state=True)
                selectedrel["rel1"] = True
            else:
                print("1 False")
                setImportColors(rel=True, val=1, state=False)
                selectedrel["rel1"] = False
            countrel["rel1"] += 1
        elif val == 2:
            if countrel["rel2"]%2 == 0:
                print("2 True")
                setImportColors(rel=True, val=2, state=True)
                selectedrel["rel2"] = True
            else:
                print("2 False")
                setImportColors(rel=True, val=2, state=False)
                selectedrel["rel2"] = False
            countrel["rel2"] += 1
        elif val == 3:
            if countrel["rel3"]%2 == 0:
                print("3")
                setImportColors(rel=True, val=3, state=True)
                selectedrel["rel3"] = True
            else:
                print("3")
                setImportColors(rel=True, val=3, state=False)
                selectedrel["rel3"] = False
            countrel["rel3"] += 1
        elif val == 4:
            if countrel["rel4"]%2 == 0:
                print("4")
                setImportColors(rel=True, val=4, state=True)
                selectedrel["rel4"] = True
            else:
                print("4")
                setImportColors(rel=True, val=4, state=False)
                selectedrel["rel4"] = False
            countrel["rel4"] += 1
        elif val == 5:
            if countrel["rel5"]%2 == 0:
                print("5")
                setImportColors(rel=True, val=5, state=True)
                selectedrel["rel5"] = True
            else:
                print("5")
                setImportColors(rel=True, val=5, state=False)
                selectedrel["rel5"] = False
            countrel["rel5"] += 1
        elif val == 6:
            if countrel["rel6"]%2 == 0:
                print("6")
                setImportColors(rel=True, val=6, state=True)
                selectedrel["rel6"] = True
            else:
                print("6")
                setImportColors(rel=True, val=6, state=False)
                selectedrel["rel6"] = False
            countrel["rel6"] += 1
        elif val == 7:
            if countrel["rel7"]%2 == 0:
                print("7")
                setImportColors(rel=True, val=7, state=True)
                selectedrel["rel7"] = True
            else:    
                print("7")
                setImportColors(rel=True, val=7, state=False)
                selectedrel["rel7"] = False
            countrel["rel7"] += 1
        elif val == 8:
            if countrel["rel8"]%2 == 0:
                print("8")
                setImportColors(rel=True, val=8, state=True)
                selectedrel["rel8"] = True
            else:
                print("8")
                setImportColors(rel=True, val=8, state=False)
                selectedrel["rel8"] = False
            countrel["rel8"] += 1
        elif val == 9:
            if countrel["relAll"]%2 == 0:
                print("True")
                setImportColors(rel=True, val=9, state=True)
                for i in selectedrel:
                    selectedrel[i] = True
                for i in countrel:
                    if i != "relAll": #skip relAll
                        countrel[i] = 1
            else:
                print("False")
                setImportColors(rel=True, val=9, state=False)
                for i in selectedrel:
                    selectedrel[i] = False
                for i in countrel:
                    if i != "relAll": #skip relAll
                        countrel[i] = 0
            countrel["relAll"] += 1

def readConfigsImportExport(IEconfig, name):
    '''Read configs for Import and Export'''
    IEconfig = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    if "win" in sys.platform:
        with open(r''+str(name)+'.ini', 'r') as configFile:
            IEconfig.read_file(configFile)   
    else:
        with open(r'/home/'+str(name)+'.ini', 'r') as configFile:
            IEconfig.read_file(configFile) 
    return IEconfig

def writeConfigs(IEconfig, name):
    '''Write configs for Import and Export'''
    if "win" in sys.platform:
        with open(r''+str(name)+'.ini', 'w') as configFile:
            IEconfig.write(configFile)   
    else:
        with open(r'/home/'+str(name)+'.ini', 'w') as configFile:
            IEconfig.write(configFile) 
    return IEconfig
''' ---------------------------- /Import and Export Page ---------------------------- '''





''' ---------------------------- On/Off Page ---------------------------- '''
def relaisOnOffPage(rel):
    """Turns the On-Off-Page on"""
    global enableOnOff
    if enableOnOff == 0: #only press once at ON / OFF, PWM or CD
        deletePWMPage()
        deleteCDPage()
        global btnRelaisOnOff_On
        global btnRelaisOnOff_Off
        
        global lblRelaisInfo
        btnRelaisOnOff_Off = addButtons(maintk, "Aus", xPos=110, yPos=392,w=75 ,h=49,cmdFunc=lambda: relaisOnOff(rel, False))
        btnRelaisOnOff_On = addButtons(maintk, "Ein", xPos=615, yPos=392, w=75 ,h=49, cmdFunc=lambda: relaisOnOff(rel, True))
        #load stats on page load
        if config["SAVE"]["Relais"+str(rel)] == "True":
            if "win" in sys.platform:
                print(rel, "HIGH")
            else:
                GPIO.output(getRelaisGPIO(rel), GPIO.HIGH)
            lblRelaisInfo = addLabelPlace(maintk, "lblRelaisPWMMinPuls", "Relais "+str(rel)+" ist eingeschaltet", xPos=250, yPos=250, fontSize=20)
            btnRelaisOnOff_On.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            btnRelaisOnOff_Off.configure_color(fg_color=fgcolor)
        else:
            if "win" in sys.platform:
                print(rel,"LOW")
            else:
                GPIO.output(getRelaisGPIO(rel), GPIO.LOW)
            lblRelaisInfo = addLabelPlace(maintk, "lblRelaisPWMMinPuls", "Relais "+str(rel)+" ist ausgeschaltet", xPos=250, yPos=250, fontSize=20)
            btnRelaisOnOff_On.configure_color(fg_color=fgcolor)
            btnRelaisOnOff_Off.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)

        enableOnOff = 1
    switchButtons(1) #turn on on-colors: onoff | pwm | cd

def relaisOnOff(rel, state):
    """Turns the Relais off or on on"""

    global lblRelaisInfo
    if state == True and not config["SAVE"]["Relais"+str(rel)] == "True":
        if "win" in sys.platform:
            print(rel, "HIGH")
        else:
            GPIO.output(getRelaisGPIO(rel), GPIO.HIGH)
        lblRelaisInfo.configure(text="Relais "+str(rel)+" ist eingeschaltet")
        btnRelaisOnOff_On.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
        btnRelaisOnOff_Off.configure_color(fg_color=fgcolor)
        writeConfig("SAVE","Relais"+str(rel), "True")
    elif state == False and not config["SAVE"]["Relais"+str(rel)] == "False":
        if "win" in sys.platform:
            print(rel, "LOW")
        else:
            GPIO.output(getRelaisGPIO(rel), GPIO.LOW)
        lblRelaisInfo.configure(text="Relais "+str(rel)+" ist ausgeschaltet")
        btnRelaisOnOff_On.configure_color(fg_color=fgcolor)
        btnRelaisOnOff_Off.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
        writeConfig("SAVE","Relais"+str(rel), "False")
            # set Config to OnOff mode
    if config["SAVE"]["Relais"+str(rel)] != "OnOff":
        writeConfig("SAVE", "Relais"+str(rel)+"_mode", "OnOff")

def deleteOnOffPage():
    """Deleting the On-Page and resets everything"""
    try:
        if lblRelaisInfo.winfo_exists(): #if exists
            global enableOnOff #global asign
            btnRelaisOnOff_On.place_forget()
            btnRelaisOnOff_Off.place_forget()
            lblRelaisInfo.place_forget()
            enableOnOff = 0 #reset value
    except NameError:   
        return
''' ---------------------------- /On/Off Page ---------------------------- '''





''' ---------------------------- /PWM Page ---------------------------- '''
def relaisPWM(rel):
    """Turns the PWM-Page on"""
    deleteOnOffPage()
    deleteCDPage()
    global pwmOn # check if pwm is already active

    if pwmOn == 0:
        global lblRelaisPWM_Puls
        global lblRelaisPWM_Pause

        global lblRelaisPWM_Name_Hour_Puls
        global btnRelaisPWM_Hour_Add_Puls
        global lblRelaisPWM_Hour_Value_Puls
        global btnRelaisPWM_Hour_Dec_Puls
        
        global lblRelaisPWM_Name_Min_Puls
        global btnRelaisPWM_Min_Dec_Puls
        global lblRelaisPWM_Min_Value_Puls
        global btnRelaisPWM_Min_Add_Puls

        global lblRelaisPWM_Name_Sec_Puls
        global btnRelaisPWM_Sec_Dec_Puls
        global lblRelaisPWM_Sec_Value_Puls
        global btnRelaisPWM_Sec_Add_Puls

        global lblRelaisPWM_Name_Hour_Pause
        global btnRelaisPWM_Hour_Add_Pause
        global lblRelaisPWM_Hour_Value_Pause
        global btnRelaisPWM_Hour_Dec_Pause
        
        global lblRelaisPWM_Name_Min_Pause
        global btnRelaisPWM_Min_Dec_Pause
        global lblRelaisPWM_Min_Value_Pause
        global btnRelaisPWM_Min_Add_Pause

        global lblRelaisPWM_Name_Sec_Pause
        global btnRelaisPWM_Sec_Dec_Pause
        global lblRelaisPWM_Sec_Value_Pause
        global btnRelaisPWM_Sec_Add_Pause

        global lblRelaisPWM_Puls_Translate_Name
        global lblRelaisPWM_Min_Translate
        global lblRelaisPWM_Sec_Translate
        global lblRelaisPWM_Puls_Translate_State

        global btnRelaisPWM_Start
        global btnRelaisPWM_Stop

        refsecPuls = config["SAVE"]["relais"+str(rel)+"ctrsecond_puls"]
        refminPuls = config["SAVE"]["relais"+str(rel)+"ctrminute_puls"]
        refhrPuls = config["SAVE"]["relais"+str(rel)+"ctrhour_puls"]

        refsecPause = config["SAVE"]["relais"+str(rel)+"ctrsecond_pause"]
        refminPause = config["SAVE"]["relais"+str(rel)+"ctrminute_pause"]
        refhrPause = config["SAVE"]["relais"+str(rel)+"ctrhour_pause"]


        lblRelaisPWM_Puls = addLabelPlace(maintk, "lblRelaisPWMPuls", "Puls", xPos=110, yPos=235, fontSize=15)
        lblRelaisPWM_Pause = addLabelPlace(maintk, "lblRelaisPWMPause", "Pause", xPos=110, yPos=325, fontSize=15)

        lblRelaisPWM_Name_Hour_Puls = addLabelPlace(maintk, "lblRelaisPWMHourPuls", "Stunden", xPos=195, yPos=205, fontSize=15)
        btnRelaisPWM_Hour_Dec_Puls = addButtons(maintk, "-", xPos=175, yPos=230, w=40, h=40, cmdFunc=lambda: decValue("pwmPuls", "hour", rel))
        lblRelaisPWM_Hour_Value_Puls = addLabelPlace(maintk, "btnRelaisPWMHourPuls", "00", xPos=225, yPos=237.5, fontSize=15)
        lblRelaisPWM_Hour_Value_Puls.configure(text=refhrPuls)
        btnRelaisPWM_Hour_Add_Puls = addButtons(maintk, "+", xPos=255, yPos=230, w=40, h=40, cmdFunc=lambda: addValue("pwmPuls", "hour", rel))

        lblRelaisPWM_Name_Min_Puls = addLabelPlace(maintk, "lblRelaisPWMMinPuls", "Minuten", xPos=360, yPos=205, fontSize=15)
        btnRelaisPWM_Min_Dec_Puls = addButtons(maintk, "-", xPos=340, yPos=230,w=40, h=40, cmdFunc=lambda: decValue("pwmPuls", "minute", rel))
        lblRelaisPWM_Min_Value_Puls = addLabelPlace(maintk, "btnRelaisPWMMinPuls", "00", xPos=390, yPos=237.5, fontSize=15)
        lblRelaisPWM_Min_Value_Puls.configure(text=refminPuls)
        btnRelaisPWM_Min_Add_Puls = addButtons(maintk, "+", xPos=420, yPos=230,w=40, h=40, cmdFunc=lambda: addValue("pwmPuls", "minute", rel))

        lblRelaisPWM_Name_Sec_Puls = addLabelPlace(maintk, "lblRelaisPWMSecPuls", "Sekunden", xPos=515, yPos=205, fontSize=15)
        btnRelaisPWM_Sec_Dec_Puls = addButtons(maintk, "-", xPos=505, yPos=230,w=40, h=40, cmdFunc=lambda: decValue("pwmPuls", "second", rel))
        lblRelaisPWM_Sec_Value_Puls = addLabelPlace(maintk, "btnRelaisPWMSecPuls", "00", xPos=555, yPos=237.5, fontSize=15)
        lblRelaisPWM_Sec_Value_Puls.configure(text=refsecPuls)
        btnRelaisPWM_Sec_Add_Puls = addButtons(maintk, "+", xPos=585, yPos=230,w=40, h=40, cmdFunc=lambda: addValue("pwmPuls", "second", rel))


        lblRelaisPWM_Name_Hour_Pause = addLabelPlace(maintk, "lblRelaisPWMHourPause", "Stunden", xPos=195, yPos=295, fontSize=15)
        btnRelaisPWM_Hour_Dec_Pause = addButtons(maintk, "-", xPos=175, yPos=320,w=40, h=40, cmdFunc=lambda: decValue("pwmPause", "hour", rel))
        lblRelaisPWM_Hour_Value_Pause = addLabelPlace(maintk, "btnRelaisPWMHourPause", "00", xPos=225, yPos=327.5, fontSize=15)
        lblRelaisPWM_Hour_Value_Pause.configure(text=refhrPause)
        btnRelaisPWM_Hour_Add_Pause = addButtons(maintk, "+", xPos=255, yPos=320,w=40, h=40, cmdFunc=lambda: addValue("pwmPause", "hour", rel))

        lblRelaisPWM_Name_Min_Pause = addLabelPlace(maintk, "lblRelaisPWMMinPause", "Minuten", xPos=360, yPos=295, fontSize=15)
        btnRelaisPWM_Min_Dec_Pause = addButtons(maintk, "-", xPos=340, yPos=320,w=40, h=40, cmdFunc=lambda: decValue("pwmPause", "minute", rel))
        lblRelaisPWM_Min_Value_Pause = addLabelPlace(maintk, "btnRelaisPWMMin", "00", xPos=390, yPos=327.5, fontSize=15)
        lblRelaisPWM_Min_Value_Pause.configure(text=refminPause)
        btnRelaisPWM_Min_Add_Pause = addButtons(maintk, "+", xPos=420, yPos=320,w=40, h=40, cmdFunc=lambda: addValue("pwmPause", "minute", rel))

        lblRelaisPWM_Name_Sec_Pause = addLabelPlace(maintk, "lblRelaisPWMSecPause", "Sekunden", xPos=515, yPos=295, fontSize=15)
        btnRelaisPWM_Sec_Dec_Pause = addButtons(maintk, "-", xPos=505, yPos=320,w=40, h=40, cmdFunc=lambda: decValue("pwmPause", "second", rel))
        lblRelaisPWM_Sec_Value_Pause = addLabelPlace(maintk, "btnRelaisPWMSecPause", "00", xPos=555, yPos=327.5, fontSize=15)
        lblRelaisPWM_Sec_Value_Pause.configure(text=refsecPause)
        btnRelaisPWM_Sec_Add_Pause = addButtons(maintk, "+", xPos=585, yPos=320,w=40, h=40, cmdFunc=lambda: addValue("pwmPause", "second", rel))

        lblRelaisPWM_Puls_Translate_Name = addLabelPlace(maintk, "lblRelaisPWMName", "", xPos=440, yPos=402, fontSize=15)
        lblRelaisPWM_Min_Translate = addLabelPlace(maintk, "lblRelaisPWMmin", "", xPos=340, yPos=392, fontSize=15)
        lblRelaisPWM_Sec_Translate = addLabelPlace(maintk, "lblRelaisPWMsec", "", xPos=340, yPos=412, fontSize=15)
        lblRelaisPWM_Puls_Translate_State = addLabelPlace(maintk, "lblRelaisPWMState", "", xPos=490, yPos=402, fontSize=15)

        btnRelaisPWM_Stop = addButtons(maintk, "Stop", xPos=110, yPos=392, w=75, h=49, cmdFunc=lambda: startMode("pwm", False, rel))
        btnRelaisPWM_Start = addButtons(maintk, "Start", xPos=615, yPos=392, w=75, h=49, cmdFunc=lambda: startMode("pwm", True, rel))

        if config["SAVE"]["Relais"+str(rel)+"ModeActivePWM"] == "True": #start funct and continue if program crashed or restarted
            startMode("pwm", True, rel)
            btnRelaisPWM_Start.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
        
        switchButtons(2) #turn on pwm-colors
        pwmOn = 1

def deletePWMPage():
    """Deleting the PWM-Page and resets everything"""
    try:
        if lblRelaisPWM_Name_Hour_Puls.winfo_exists(): #if exists
            global pwmOn #global asign

            lblRelaisPWM_Puls.place_forget()
            lblRelaisPWM_Pause.place_forget()

            lblRelaisPWM_Name_Hour_Puls.place_forget()
            btnRelaisPWM_Hour_Add_Puls.place_forget()
            lblRelaisPWM_Hour_Value_Puls.place_forget()
            btnRelaisPWM_Hour_Dec_Puls.place_forget()

            lblRelaisPWM_Name_Min_Puls.place_forget()
            btnRelaisPWM_Min_Dec_Puls.place_forget()
            lblRelaisPWM_Min_Value_Puls.place_forget()
            btnRelaisPWM_Min_Add_Puls.place_forget()

            lblRelaisPWM_Name_Sec_Puls.place_forget()
            btnRelaisPWM_Sec_Dec_Puls.place_forget()
            lblRelaisPWM_Sec_Value_Puls.place_forget()
            btnRelaisPWM_Sec_Add_Puls.place_forget()


            lblRelaisPWM_Name_Hour_Pause.place_forget()
            btnRelaisPWM_Hour_Add_Pause.place_forget()
            lblRelaisPWM_Hour_Value_Pause.place_forget()
            btnRelaisPWM_Hour_Dec_Pause.place_forget()
            
            lblRelaisPWM_Name_Min_Pause.place_forget()
            btnRelaisPWM_Min_Dec_Pause.place_forget()
            lblRelaisPWM_Min_Value_Pause.place_forget()
            btnRelaisPWM_Min_Add_Pause.place_forget()

            lblRelaisPWM_Name_Sec_Pause.place_forget()
            btnRelaisPWM_Sec_Dec_Pause.place_forget()
            lblRelaisPWM_Sec_Value_Pause.place_forget()
            btnRelaisPWM_Sec_Add_Pause.place_forget()

            lblRelaisPWM_Puls_Translate_Name.place_forget()
            lblRelaisPWM_Min_Translate.place_forget()
            lblRelaisPWM_Sec_Translate.place_forget()
            lblRelaisPWM_Puls_Translate_State.place_forget()

            btnRelaisPWM_Start.place_forget()
            btnRelaisPWM_Stop.place_forget()
            pwmOn = 0 #reset value
    except NameError:   
        return

def pwmTimer(stop_event, arg, rel, refvalPuls, refvalPause):
    '''set up the pwm timer'''
    while not stop_event.wait(0):
        if "win" in sys.platform:
            print(rel, "HIGH")
        else:
            GPIO.output(getRelaisGPIO(rel), GPIO.HIGH)
        writeConfig("SAVE", "Relais"+str(rel), "True")
        print(rel, "RELAIS ON") # GET RELAIS ON HERE

        for i in range(1, refvalPuls+1): #start at 1 end at refvalpuls + 1
            if stop_event.wait(1): #if triggered quit
                break
            calcValuePuls = calcCDTimeLeft(refvalPuls-i)
            if rel == currOpenedRelais:
                lblRelaisPWM_Puls_Translate_State.configure(text="Aus") #set off in the same sec as the timeleft
                lblRelaisPWM_Puls_Translate_Name.configure(text="bis") # set bis in the same sec as the timeleft
                lblRelaisPWM_Min_Translate.configure(text=str((int(calcValuePuls[0])*60)+(int(calcValuePuls[1]))+(int(calcValuePuls[2])/60).__round__(1))+" Min.")
                lblRelaisPWM_Sec_Translate.configure(text=str((int(calcValuePuls[0])*60*60)+(int(calcValuePuls[1])*60)+(int(calcValuePuls[2])))+" Sek.")
        if "win" in sys.platform:
            print(rel, "LOW")
        else:
            GPIO.output(getRelaisGPIO(rel), GPIO.LOW)
        writeConfig("SAVE", "Relais"+str(rel), "False")
        print("RELAIS OFF") # GET RELAIS OFF HERE
        for i in range(1, refvalPause+1):
            if stop_event.wait(1): #if triggered quit
                break
            calcValuePause = calcCDTimeLeft(refvalPause-i)
            if rel == currOpenedRelais:
                lblRelaisPWM_Puls_Translate_State.configure(text="Ein")
                lblRelaisPWM_Puls_Translate_Name.configure(text="bis") # set bis in the same sec as the timeleft
                lblRelaisPWM_Min_Translate.configure(text=str((int(calcValuePause[0])*60)+(int(calcValuePause[1]))+(int(calcValuePause[2])/60).__round__(1))+" Min.")
                lblRelaisPWM_Sec_Translate.configure(text=str((int(calcValuePause[0])*60*60)+(int(calcValuePause[1])*60)+(int(calcValuePause[2])))+" Sek.")
''' ---------------------------- /PWM Page ---------------------------- '''





''' ---------------------------- CD Page ---------------------------- '''
def switchCDOnOff(rel):
    '''Change on CD Page ON and OFF states for the Countdown timer'''
    global btnRelaisCD_OnOff # under here, deleting button and creating it again, because of color background bug. it wouldnt change too
    global btnRelaisCD_ChangeRelaisState

    btnRelaisCD_OnOff.place_forget()
    btnRelaisCD_ChangeRelaisState.place_forget()

    btnRelaisCD_OnOff = addButtons(maintk, "Ein", xPos=615, yPos=320, w=75, h=49, cmdFunc=lambda: switchCDOnOff(rel))
    btnRelaisCD_ChangeRelaisState = addButtons(maintk, "", xPos=340, yPos=392,w=120, h=49, cmdFunc=print)
    if config["SAVE"]["relais"+str(rel)] == "True":
        btnRelaisCD_OnOff.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
        btnRelaisCD_OnOff.set_text("Ein")

        btnRelaisCD_ChangeRelaisState.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        btnRelaisCD_ChangeRelaisState.set_text("ist Aus")
        writeConfig("SAVE", "relais"+str(rel), "False")
        if "win" in sys.platform:
            print(rel, "LOW")
        else:
            GPIO.output(getRelaisGPIO(rel), GPIO.LOW)
    else:
        btnRelaisCD_OnOff.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
        btnRelaisCD_OnOff.set_text("Aus")

        btnRelaisCD_ChangeRelaisState.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
        btnRelaisCD_ChangeRelaisState.set_text("ist Ein")
        writeConfig("SAVE", "relais"+str(rel), "True")
        if "win" in sys.platform:
            print(rel, "HIGH")
        else:
            GPIO.output(getRelaisGPIO(rel), GPIO.HIGH)

def relaisCD(rel):
    """Turns the CD-Page on"""
    deleteOnOffPage()
    deletePWMPage()

    global cdOn # check if cd is already active
    if cdOn == 0:
        global lblRelaisCD

        global lblRelaisCD_Name_Hour
        global btnRelaisCD_Hour_Dec
        global lblRelaisCD_Hour_Value
        global btnRelaisCD_Hour_Add

        global lblRelaisCD_Name_Min
        global btnRelaisCD_Min_Dec
        global lblRelaisCD_Min_Value
        global btnRelaisCD_Min_Add

        global lblRelaisCD_Name_Sec
        global btnRelaisCD_Sec_Dec
        global lblRelaisCD_Sec_Value
        global btnRelaisCD_Sec_Add

        global lblRelaisCD_CD_To
        global lblRelaisCD_CD
        global lblRelaisCD_CD_Info
        global btnRelaisCD_OnOff
        global btnRelaisCD_ChangeRelaisState

        global btnRelaisCD_Start
        global btnRelaisCD_Stop


        refsec = config["SAVE"]["relais"+str(rel)+"ctrsecond_cd"]
        refmin = config["SAVE"]["relais"+str(rel)+"ctrminute_cd"]
        refhr = config["SAVE"]["relais"+str(rel)+"ctrhour_cd"]

        lblRelaisCD = addLabelPlace(maintk, "lblRelaisCD", "CD", xPos=110, yPos=235, fontSize=15)

        lblRelaisCD_Name_Hour = addLabelPlace(maintk, "lblRelaisCDHour", "Stunden", xPos=195, yPos=205, fontSize=15)
        btnRelaisCD_Hour_Dec = addButtons(maintk, "-", xPos=175, yPos=230,w=40, h=40, cmdFunc=lambda: decValue("cd", "hour", rel))
        lblRelaisCD_Hour_Value = addLabelPlace(maintk, "btnRelaisCDHour", "00", xPos=225, yPos=237.5, fontSize=15)
        lblRelaisCD_Hour_Value.configure(text= refhr)
        btnRelaisCD_Hour_Add = addButtons(maintk, "+", xPos=255, yPos=230,w=40, h=40, cmdFunc=lambda: addValue("cd", "hour", rel))

        lblRelaisCD_Name_Min = addLabelPlace(maintk, "lblRelaisCDMin", "Minuten", xPos=360, yPos=205, fontSize=15)
        btnRelaisCD_Min_Dec = addButtons(maintk, "-", xPos=340, yPos=230,w=40, h=40, cmdFunc=lambda: decValue("cd", "minute", rel))
        lblRelaisCD_Min_Value = addLabelPlace(maintk, "btnRelaisCDMin", "00", xPos=390, yPos=237.5, fontSize=15)
        lblRelaisCD_Min_Value.configure(text=refmin)
        btnRelaisCD_Min_Add = addButtons(maintk, "+", xPos=420, yPos=230,w=40, h=40, cmdFunc=lambda: addValue("cd", "minute", rel))

        lblRelaisCD_Name_Sec = addLabelPlace(maintk, "lblRelaisCDSec", "Sekunden", xPos=515, yPos=205, fontSize=15)
        btnRelaisCD_Sec_Dec = addButtons(maintk, "-", xPos=505, yPos=230,w=40, h=40, cmdFunc=lambda: decValue("cd", "second", rel))
        lblRelaisCD_Sec_Value = addLabelPlace(maintk, "btnRelaisCDSec", "00", xPos=555, yPos=237.5, fontSize=15)
        lblRelaisCD_Sec_Value.configure(text=refsec)
        btnRelaisCD_Sec_Add = addButtons(maintk, "+", xPos=585, yPos=230,w=40, h=40, cmdFunc=lambda: addValue("cd", "second", rel))

        lblRelaisCD_CD_To = addLabelPlace(maintk, "btnRelaisCDCDTo", "bis", xPos=505, yPos=320, fontSize=15)
        lblRelaisCD_CD = addLabelPlace(maintk, "btnRelaisCDCD", "00:00:00", xPos=340, yPos=320, fontSize=15)
        lblRelaisCD_CD.configure(text=calcNullPosition(int(refhr),int(refmin),int(refsec)))
        lblRelaisCD_CD_Info = addLabelPlace(maintk, "btnRelaisCDCD", "hh:mm:ss", xPos=345, yPos=350, fontSize=10)

        btnRelaisCD_OnOff = addButtons(maintk, "Ein", xPos=615, yPos=320, w=75, h=49, cmdFunc=lambda: switchCDOnOff(rel))
        btnRelaisCD_ChangeRelaisState = addButtons(maintk, "ist Ein", xPos=340, yPos=392,w=120, h=49, cmdFunc=print)

        if config["SAVE"]["relais"+str(rel)] == "True":
            btnRelaisCD_OnOff.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
            btnRelaisCD_OnOff.set_text("Aus")
            btnRelaisCD_ChangeRelaisState.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            btnRelaisCD_ChangeRelaisState.set_text("ist Ein")
        else:
            btnRelaisCD_OnOff.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
            btnRelaisCD_OnOff.set_text("Ein")
            btnRelaisCD_ChangeRelaisState.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)
            btnRelaisCD_ChangeRelaisState.set_text("ist Aus")
            
        btnRelaisCD_Start = addButtons(maintk, "Start", xPos=615, yPos=392, w=75, h=49, cmdFunc=lambda: startMode("cd",True, rel))
        btnRelaisCD_Stop = addButtons(maintk, "Stop", xPos=110, yPos=392, w=75, h=49, cmdFunc=lambda: startMode("cd", False, rel))

        if config["SAVE"]["Relais"+str(rel)+"ModeActiveCD"] == "True": #start funct and continue if program crashed or restarted
            startMode("cd",True, rel)
            btnRelaisCD_Start.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)

        switchButtons(3) #turn on cd-colors
        cdOn = 1

def refreshCDRelais(rel):
    '''get updated values of cd on / off button'''
    global btnRelaisCD_ChangeRelaisState
    global btnRelaisCD_OnOff

    if config["SAVE"]["relais"+str(rel)] == "True":
        btnRelaisCD_OnOff.place_forget()
        btnRelaisCD_OnOff = addButtons(maintk, "Aus", xPos=615, yPos=320, w=75, h=49, cmdFunc=lambda: switchCDOnOff(rel))
        btnRelaisCD_OnOff.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)

        btnRelaisCD_ChangeRelaisState.place_forget()
        btnRelaisCD_ChangeRelaisState = addButtons(maintk, "ist Ein", xPos=340, yPos=392,w=120, h=49, cmdFunc=print)
        btnRelaisCD_ChangeRelaisState.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)
    else:
        btnRelaisCD_OnOff.place_forget()
        btnRelaisCD_OnOff = addButtons(maintk, "Ein", xPos=615, yPos=320, w=75, h=49, cmdFunc=lambda: switchCDOnOff(rel))
        btnRelaisCD_OnOff.configure_color(fg_color=fgcolorPressed, hover_color=fgcolorPressedHover)

        btnRelaisCD_ChangeRelaisState.place_forget()
        btnRelaisCD_ChangeRelaisState = addButtons(maintk, "ist Aus", xPos=340, yPos=392,w=120, h=49, cmdFunc=print)
        btnRelaisCD_ChangeRelaisState.configure_color(fg_color=fgcolor, hover_color=fgcolorHover)

def cdTimer(stop_event, arg, rel, timeleft):
    '''start countdown timer'''
    while not stop_event.wait(0):
        for i in range(timeleft):
            timeleft -= 1
            writeConfig("SAVE","relais"+str(rel)+"timecdleft", str(timeleft))
            calcValue = calcCDTimeLeft(timeleft)
            if rel == currOpenedRelais:
                try: #if timer is already 0 after restart gives nameerror
                    lblRelaisCD_CD.configure(text=calcNullPosition(calcValue[0], calcValue[1], calcValue[2]))
                except NameError:
                    pass
            if stop_event.wait(1):
                break
        print(rel,"stops")
        if timeleft <= 0:
            if config["SAVE"]["relais"+str(rel)] != "True":  # GET RELAIS HERE OFF OR ON
                if "win" in sys.platform:
                    print(rel, "HIGH")
                else:
                    GPIO.output(getRelaisGPIO(rel), GPIO.HIGH)
                writeConfig("SAVE", "Relais"+str(rel), "True")
                print("RELAIS ON")
                break
            else:
                if "win" in sys.platform:
                    print(rel, "LOW")
                else:
                    GPIO.output(getRelaisGPIO(rel), GPIO.LOW)
                writeConfig("SAVE", "Relais"+str(rel), "False")
                print("RELAIS OFF")
                break
        else:
            break

def deleteCDPage():
    """Deleting the CD-Page and resets everything"""
    try:
        if lblRelaisCD.winfo_exists(): #if exists
            global cdOn #global asign

            lblRelaisCD.place_forget()

            lblRelaisCD_Name_Hour.place_forget()
            btnRelaisCD_Hour_Dec.place_forget()
            lblRelaisCD_Hour_Value.place_forget()
            btnRelaisCD_Hour_Add.place_forget()

            lblRelaisCD_Name_Min.place_forget()
            btnRelaisCD_Min_Dec.place_forget()
            lblRelaisCD_Min_Value.place_forget()
            btnRelaisCD_Min_Add.place_forget()

            lblRelaisCD_Name_Sec.place_forget()
            btnRelaisCD_Sec_Dec.place_forget()
            lblRelaisCD_Sec_Value.place_forget()
            btnRelaisCD_Sec_Add.place_forget()

            lblRelaisCD_CD_To.place_forget()
            lblRelaisCD_CD.place_forget()
            lblRelaisCD_CD_Info.place_forget()
            btnRelaisCD_OnOff.place_forget()
            btnRelaisCD_ChangeRelaisState.place_forget()

            btnRelaisCD_Start.place_forget()
            btnRelaisCD_Stop.place_forget()
            cdOn = 0 #reset value
    except NameError:   
        return
''' ---------------------------- /CD Page ---------------------------- '''





''' ---------------------------- Main ---------------------------- '''
readConfig() # init config
initTitle(maintk)
initHeadButtons(maintk)
checkRelaisStates() #on boot
relaisPage(1) #start at relais 1

'''setup current time'''
clock = Label(maintk, font=('Century Gothic', 15), bg='white')
clock.place(x=305,y=4) # not working problably
clockTick()
'''/setup current time'''

maintk.mainloop() #start looping tkinter ui
''' ---------------------------- /Main ---------------------------- '''