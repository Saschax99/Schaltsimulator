def calcNullPosition(ctrHr_CD, ctrMin_CD, ctrSec_CD):
    '''calculate null positions for correct time in cd page'''
    if ctrHr_CD <= 9 and ctrMin_CD <= 9 and ctrSec_CD <= 9: # 1 1 1
        valStr = "0"+str(ctrHr_CD)+":"+"0"+str(ctrMin_CD)+":"+"0"+str(ctrSec_CD)
        return valStr
    elif ctrHr_CD <= 9 and ctrMin_CD <= 9: # 1 1 0
        valStr = "0"+str(ctrHr_CD)+":"+"0"+str(ctrMin_CD)+":"+str(ctrSec_CD)
        return valStr
    elif ctrHr_CD <= 9 and ctrSec_CD <= 9: # 1 0 1
        valStr = "0"+str(ctrHr_CD)+":"+str(ctrMin_CD)+":"+"0"+str(ctrSec_CD)
        return valStr
    elif ctrMin_CD <= 9 and ctrSec_CD <= 9: # 0 1 1
        valStr = str(ctrHr_CD)+":"+"0"+str(ctrMin_CD)+":"+"0"+str(ctrSec_CD)
        return valStr
    elif ctrHr_CD <= 9: # 1 0 0
        valStr = "0"+str(ctrHr_CD)+":"+str(ctrMin_CD)+":"+str(ctrSec_CD)
        return valStr
    elif ctrMin_CD <= 9: # 0 1 0
        valStr = str(ctrHr_CD)+":"+"0"+str(ctrMin_CD)+":"+str(ctrSec_CD)
        return valStr
    elif ctrSec_CD <= 9: # 0 0 1
        valStr = str(ctrHr_CD)+":"+str(ctrMin_CD)+":"+"0"+str(ctrSec_CD)
        return valStr
    if ctrHr_CD >= 10 and ctrMin_CD >= 10 and ctrSec_CD >= 10:
        valStr = str(ctrHr_CD)+":"+str(ctrMin_CD)+":"+str(ctrSec_CD)
        return valStr

def calcCDTimeLeft(timeleft):
    '''calculate time left from seconds to hours, minutes and seconds'''
    timeleftHr = 0
    timeleftMin = 0
    timeleftSec = 0
    print(timeleft)
    while timeleft >= 0:
        print(timeleft)
        if timeleft >= 60: #if larger than
            timeleft -= 60 # add 1 minute under
            if timeleftMin >= 59: #
                timeleftHr += 1
                timeleftMin -= 59 #-60 + 1
            else:    
                timeleftMin += 1
        else:
            timeleftSec = timeleft
            return [timeleftHr, timeleftMin, timeleftSec]

def checkSelectedRelais(relList):
    '''Check if Relais were selected'''
    for i in relList:
        if relList[i] == True:
            return True
    return False

def configvalues(rel):
    '''get configvalues for each relais'''
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
    return my_list