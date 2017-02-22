import telnetlib
import string
import sys
import datetime
import os

from time import sleep
from sys import stderr

PROMSTR = '1 # '

def GetTestDurationTime(startTime, endTime, f, flag, i):
    interval = endTime - startTime
    if (flag == 'case'):
        msg = 'Test case-' + str(i)
    elif (flag == 'bucket'):
        msg = 'Test bucket' 
    msg = msg + ' Starting Time:' + str(startTime) + '; Ending Time:' + str(endTime) + ';Duration Time:' + str(interval) 
    logMsg (msg, 'BAT_MSG', f)

def CreateLogFile(scriptName, testMachine):
    pstr='%Y%m%d_%H%M_%S'
    testStartTime = datetime.datetime.now().strftime(pstr)
    logName = scriptName + '_' + testMachine + '_' + testStartTime
    f = file(logName, 'w')
    return (f, logName)

def TransformLogFile(logName, logDir):
    logName_bak = logName + ".log"
    cmd = "cat \"" + logName + "\" | tr -d \"\\r\" > \"" + logName_bak + "\"" 
    cmd_1 = "rm -f \"" + logName + "\""
    os.system (cmd)
    os.system (cmd_1)
    cmd_2 = 'mv ' + logName_bak + ' ' + logDir
    os.system (cmd_2)
	
def TelentToCEC(SharkAddr, sharkPort, f):
    usr        = 'root'
    psw        = 'r00t'
    SharkPort0 = 12301
    
    global PROMSTR
    
    try:
        t = telnetlib.Telnet(SharkAddr, sharkPort,0x7fffffff)
    except:
        stderr.write('Network exception! Pls check it.')
        return (1, t)
    
    ostr = t.read_until('Login:')

    t.write(usr + '\n')
    ostr = t.read_until('Password:')
    
    t.write(psw + '\n')
    ostr = t.read_until('1 # ')
    ostr_element = ostr.split('\n')
    PROMSTR = ostr_element[-1]
    
    return (0, t)

def CheckHAStatus(f, t):
    msg  = 'Executing command: lsrsrc -s state!=0 IBM.EssHA'
    logMsg (msg, 'KEY_MSG', f)
    cmd  = 'date;lsrsrc -s state!=0 IBM.EssHA' + '\n'
    ostr = ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')
    haStatus = 0
    for i in range(1, len(ostr_element) - 1):
        if ('resource' in ostr_element[i]):
            haStatus = 1
            break
    return haStatus

def CheckDAStatus(f, t):
    msg = 'Executing command: lsrsrc -s state!=0 IBM.EssDA'
    logMsg (msg, 'KEY_MSG', f)
    cmd = 'date;lsrsrc -s state!=0 IBM.EssDA' + '\n'
    ostr = ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')
    daStatus = 0
    for i in range(1, len(ostr_element) - 1):
        if ('resource' in ostr_element[i]):
            daStatus = 1
            break
    return daStatus

def CheckEnclosureStatus(f,t):
    msg = 'Executing command: lsdev -Cl enc*'
    logMsg (msg, 'KEY_MSG', f)
    cmd = 'date;lsdev -Cl enc*' 
    ostr = ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')
    seStatus = 0
    for i in range(1, len(ostr_element) - 1):
        if ('Defined' in ostr_element[i]):
            seStatus = 1
            break
    return seStatus 


def machineStatusCheck(t, f):
    msg = 'Executing command: cat /dev/cpss0/status/opmode'
    logMsg (msg, 'KEY_MSG', f)
    cmd = 'date; cat /dev/cpss0/status/opmode' + '\n'
    ostr = ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')

    clusterMode = 1
    for i in range(1, len(ostr_element) - 1):
	if (('CurEnv' in ostr_element[i]) and ('Dual Cluster Operational' in ostr_element[i])):
	    clusterMode = 0
	    break
    return clusterMode

def CheckIfCardFenced(t, f, adapter):
    msg = 'Executing command: cat /dev/cpss0/status/' + adapter
    logMsg(msg, 'KEY_MSG', f)
    cmd = 'date; cat /dev/cpss0/status/' + adapter + '\n'
    ostr = ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')
    isAdapterFenced = 1
    for i in range(0, len(ostr_element)):
        if('FENCED' in ostr_element[i]):
            isAdapterFenced = 0
            break
    return isAdapterFenced

def CheckIfAdapterExist(t, f, adapter):
    msg = 'Executing command: lsdev -Cc adapter'
    logMsg(msg, 'KEY_MSG', f)
    cmd = 'lsdev -Cc adapter\n'
    ostr = ExecuteCmd(cmd, t, f)
    ostr_element   = ostr.split('\n')
    isAdapterExist = 0
    for i in range(0, len(ostr_element)):
        if (adapter in ostr_element[i]):
            isAdapterExist = 1
            break
    return isAdapterExist


def logMsg(msg, debugLevel, f):
    # add '\n' char of the message if it does not end with '\n' 
    if (msg[-1] != '\n'):
        msg = msg + '\n'
        
    if (debugLevel == 'KEY_MSG'):
        print('\n\n*****************************************************************\n')
        print(msg)
        print('*****************************************************************\n\n')
        
        f.write('\n\n*****************************************************************\n')
        f.write(msg)
        f.write('*****************************************************************\n\n')
    elif(debugLevel == 'MACHINE_MSG'):
        print(msg)
        f.write(msg)
    elif(debugLevel == 'BAT_MSG'):
        print('\n\n################################################################\n')
        print(msg)
        print('##################################################################\n\n')
        
        f.write('\n\n###############################################################\n')
        f.write(msg)
        f.write('###############################################################\n\n')
    else:
        msg = '@@@@debug@@@@' + msg + '\n'
        print(msg)
        f.write(msg)
    
def ScriptFailHandler(f, logName, logDir):
    msg = 'Test Failure!'
    logMsg(msg, 'KEY_MSG', f)
    f.close()
    TransformLogFile(logName, logDir)
    exit(1)

def ScriptPassHandler(f, logName, logDir):
    msg = 'Test Passed!'
    logMsg(msg, 'KEY_MSG', f)
    f.close()
    TransformLogFile(logName, logDir)
    exit (0)

def ExecuteCmd(cmd, t, f):
    # add '\n' char to the end of cmd if cmd doesn't end with '\n'
    if('date' not in cmd):
        cmd = 'date;' + cmd
    if(cmd[-1] != '\n'):
        cmd = cmd + '\n'
    if (len(cmd) > 60):
        t.write(cmd)
        ostr_1 = t.read_until('\n')
        ostr   = PROMSTR + cmd + t.read_until(PROMSTR)
        logMsg(ostr, 'MACHINE_MSG', f)
    else:
        t.write(cmd)
        ostr = PROMSTR + t.read_until(PROMSTR)
        logMsg(ostr, 'MACHINE_MSG', f)

    return ostr









