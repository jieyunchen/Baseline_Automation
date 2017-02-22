#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telnetlib
import string
import sys
import datetime
import os
from time import sleep
from sys import stderr

sys.path.append('/home/root/BAT/lib')
import public_interface


def executeRASRepairCmd(t, f, cmd, flag):
    msg = 'Executing command: ' + cmd
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'date;' + cmd + ';' + "echo \"exitcode:$?\"" + '\n'
    ostr = public_interface.ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')
    exitCode     = 1
    retCode      = 1
    for i in range(0, len(ostr_element)):
        if ('exitcode:0' in ostr_element[i]):
            exitCode = 0
        if ('returnCode = 0' in ostr_element[i]):
            retCode  = 0
    
    if(flag == 0):
        return exitCode
    else:
        return ((exitCode == 0) and (retCode == 0))


if __name__ == '__main__':
    
    # Check if the input arguments are valid
    
    logDir = '/home/root/BAT/log' 
    argc = len(sys.argv)
    if ((argc != 5) and (argc != 7)):
        print 'usage sample: fencevraDA.py -t mbxx -c vraxxx'
        exit (1)
        
    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb15' and sys.argv[2] != 'mb16') or
         (sys.argv[3] != '-c') or
         ('vra' not in sys.argv[4])
         ):
        print 'usage sample: fencevraDA.py -t mbxx -c vraxxx'
        exit (1)

    if ((argc == 7) and (sys.argv[5] == '-d')):
        logDir = sys.argv[6]

    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'
    SharkPort0 = 12301
    SharkPort1 = 12311
    vraAdapter = sys.argv[4]
 
    (f, logName) = public_interface.CreateLogFile(sys.argv[0], sys.argv[2])

    # log into CEC
    msg = 'Connecting to ' + SharkAddr + ',' + 'port ' + str(SharkPort0)
    public_interface.logMsg(msg, 'KEY_MSG', f)
    (returnCode, t) = public_interface.TelentToCEC(SharkAddr, SharkPort0, f)
    if (returnCode == 1):
        msg = 'Failed to telnet to ' + SharkAddr
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Telnet to ' + SharkAddr + ' successfully!'
        public_interface.logMsg(msg, 'KEY_MSG', f)

    #Check which CEC to run fence/repair VRA adapter inject
    msg = 'Checking which CEC owns the VRA adapter'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'davra -Q SISHARVEST -q WARHAWKS bUseCache=FALSE' + '\n'
    ostr = public_interface.ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split ('\n')
    flag_vra     = 0
    for i in range(0, len(ostr_element)):
        if (vraAdapter in ostr_element[i]):
            flag_vra = 1
            break
    if (flag_vra == 0):
        msg = 'VRA adapter ' + vraAdapter + ' is not existed in DS8K ' + SharkAddr
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        VRA_str = ostr_element[i].strip()
       
    #Telnet to CEC1 if CEC1 owns VRA adapter
    if (VRA_str[-1] == '1'):
        t.close()
        (returnCode, t) = public_interface.TelentToCEC(SharkAddr, SharkPort1, f)
        if (returnCode == 1):
            msg = 'Failed to telnet to ' + SharkAddr
            public_interface.logMsg(msg, 'KEY_MSG', f)
            public_interface.ScriptFailHandler(f, logName, logDir)
        else:
            msg = 'Telnet to ' + SharkAddr + ' successfully!'
            public_interface.logMsg(msg, 'KEY_MSG', f)

    # Check DS8K machine status before test starts -- check if DS8K is in dual cluster mode
    msg = 'Check DS8K machine status before starting test'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    clusterMode = public_interface.machineStatusCheck(t, f)
    if (clusterMode == 1):
        msg = SharkAddr + ' is not in dual cluster mode, please check machine status before starting the test'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Machine status of ' + SharkAddr + ' is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        
    #Check DA status before test starts
    msg = 'Check status of DA adapters before test starts'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if (public_interface.CheckDAStatus(f, t) == 1):
        msg = 'Not all DA adapter is available, please check the status of DA adapter before running test'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Status of all DA adapters is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)

    #Fence VRA adapter
    cmd = '/CPSS/testdaemon -l ' + vraAdapter + ' -4'
    cmd = 'date;' + cmd + ';' + '\n'
    ostr = public_interface.ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')
    fenceOpsFlag = 1
    for i in range(0, len(ostr_element)):
        if('response information: 0 0 0' in ostr_element[i]):
            fenceOpsFlag = 0
            break
    if(fenceOpsFlag != 0):
        msg = 'Fence Vraid Adapter ' + vraAdapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    #Sleep one minute to check if the VRAID adapter is fenced
    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)

    #Check the status of VRA adapter
    msg = 'Check if the status of Vraid adapter ' +  vraAdapter + ' has been fenced'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if(public_interface.CheckIfCardFenced(t, f, vraAdapter) != 0):
        msg = 'Vraid adapter ' + vraAdapter + ' has not been fenced, pls check status of this Vraid adapter before test'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Vraid adapter ' + vraAdapter + ' has been fenced'
        public_interface.logMsg(msg, 'KEY_MSG', f)
     
    #Execute RAS repair command to repair VRA adapter
    cmd = "runact -s \'logicalName==\"" + vraAdapter + "\"\' IBM.EssDA applicationLevelDeactivateRepair"
    if(executeRASRepairCmd(t, f, cmd, 0) != 0):
        msg = 'Execute applicationLevelDeactivateRepair for VRA adapter ' + vraAdapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)

    cmd = "runact -s \'logicalName==\"" + vraAdapter + "\"\' IBM.EssDA systemLevelActivateRepair"
    if(executeRASRepairCmd(t, f, cmd, 0) != 0):
        msg = 'Execute systemLevelActivateRepair for VRA adapter ' + vraAdapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)

    cmd = "runact -s \'logicalName==\"" + vraAdapter + "\"\' IBM.EssDA systemLevelVerifyRepair"
    if(executeRASRepairCmd(t, f, cmd, 0) != 0):
        msg = 'Execute systemLevelVerifyRepair for VRA adapter ' + vraAdapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)

    cmd = "runact -s \'logicalName==\"" + vraAdapter + "\"\' IBM.EssDA applicationLevelActivateRepair"
    if(executeRASRepairCmd(t, f, cmd, 0) != 0):
        msg = 'Execute applicationLevelActivateRepair for VRA adapter ' + vraAdapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)

    cmd = "runact -s \'logicalName==\"" + vraAdapter + "\"\' IBM.EssDA resetDATakeover"
    if(executeRASRepairCmd(t, f, cmd, 1) == False):
        msg = 'Execute resetDATakeover for VRA adapter ' + vraAdapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)
        
    #Check DA status after test completes
    msg = 'Check status of DA adapters after test completes'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if (public_interface.CheckDAStatus(f, t) == 1):
        msg = 'Not all DA adapter is available, please check the status of DA adapter'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Status of all DA adapters is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)

    # Check DS8K machine status after test completes -- check if DS8K is in dual cluster mode
    msg = 'Check DS8K machine status after test completes'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    clusterMode = public_interface.machineStatusCheck(t, f)
    if (clusterMode == 1):
        msg = SharkAddr + ' is not in dual cluster mode'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Machine status of ' + SharkAddr + ' is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)

    public_interface.ScriptPassHandler(f, logName, logDir)    
    
