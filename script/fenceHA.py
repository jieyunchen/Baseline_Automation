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


def executeRASRepairCmd(t, f, cmd):
    msg = 'Executing cmd: ' + cmd
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'date;' + cmd + ';' + "echo \"exitcode:$?\"" + '\n'
    ostr = public_interface.ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')
    exitCode = 1
    retCode  = 1
    for i in range(0, len(ostr_element)):
        if ('returnCode  = 0' in ostr_element[i]):
            retCode  = 0
        if ('errorNumber = 0' in ostr_element[i]):
            exitCode = 0
    if ((retCode == 0) and (exitCode == 0)):
        return 0
    else:
        return 1
    
if __name__ == '__main__':
    
    # Check if the input arguments are valid
    logDir = '/home/root/BAT/log'

    argc = len(sys.argv)

    if ((argc != 5) and (argc != 7)):
        print 'usage sample: fenceHA.py -t mbxx -c cpssfcxxx'
        exit (1)
    
    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16' and sys.argv[2] != 'mb15' and sys.argv[2] != 'mb17') or
         (sys.argv[3] != '-c') or
         ('cpssfc' not in sys.argv[4]) 
         ):
        print 'usage sample: fenceHA.py -t mbxx -c cpssfcxxx'
        exit (1)
        
    if ((argc == 7) and (sys.argv[5] == '-d')):
        logDir = sys.argv[6]

    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'
    HA_adapter = sys.argv[4]
    sharkPort  = 12301

    (f, logName) = public_interface.CreateLogFile(sys.argv[0], sys.argv[2])

    # log into CEC
    msg = 'Connecting to ' + SharkAddr + ',' + 'port ' + str(sharkPort)
    public_interface.logMsg(msg, 'KEY_MSG', f)
    (returnCode, t) = public_interface.TelentToCEC(SharkAddr, sharkPort, f)
    if (returnCode == 1):
        msg = 'Failed to telnet to ' + SharkAddr
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Telnet to ' + SharkAddr + ' successfully!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        
    # Check if HA adapter exists in DS8K
    msg = 'Check if HA adapter exists in DS8K before starting test'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if (public_interface.CheckIfAdapterExist(t, f, HA_adapter) == 0):
        msg = HA_adapter + ' is not existed in DS8K'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

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

    #Check HA status before test starts
    msg = 'Check status of HA adapters before test starts'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if (public_interface.CheckHAStatus(f, t) == 1):
        msg = 'Not all HA adapter is available, please check the status of HA adapter before running test'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Status of all HA adapters is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)

        
    #Fence HA adapter
    msg = 'Start to fence HA adapter ' + HA_adapter + ', need to wait 15 minutes...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'date;' + '/fenceHA ' + HA_adapter + ';' + "echo \"exitcode:$?\"" + '\n'
    ostr = public_interface.ExecuteCmd(cmd, t, f)
    ostr_element = ostr.split('\n')
    exitCode     = 1
    for i in range(0, len(ostr_element)):
        if ('exitcode:0' in ostr_element[i]):
            exitCode = 0
            break

    if(exitCode == 1):
        msg = 'Execute fence HA adapter ' + HA_adapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    #Sleep one minute to check if HA adapter is fenced
    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)

    #Check HA status again to see if HA card has been fenced
    msg = 'Check status of HA adapter ' +  HA_adapter + ' is fenced or not'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if(public_interface.CheckIfCardFenced(t, f, HA_adapter) != 0):
        msg = 'HA adapter ' + HA_adapter + ' has not been fenced, pls check status of this HA adapter first'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'HA adapter ' +  HA_adapter + ' has been fenced'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        
    #Execute RAS repair command to repair HA adapter
    msg = 'Start to repair HA adapter ' + HA_adapter
    public_interface.logMsg(msg, 'KEY_MSG', f)
    
    cmd = "runact -s \'logicalName==\"" + HA_adapter + "\"\' IBM.EssHA applicationLevelDeactivate"
    if(executeRASRepairCmd(t, f, cmd) != 0):
        msg = 'Execute applicationLevelDeactivate for HA adapter ' + HA_adapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)

    cmd = "runact -s \'logicalName==\"" + HA_adapter + "\"\' IBM.EssHA systemLevelActivateRepair"
    if(executeRASRepairCmd(t, f, cmd) != 0):
        msg = 'Execute systemLevelActivateRepair for HA adapter ' + HA_adapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)
    
    cmd = "runact -s \'logicalName==\"" + HA_adapter + "\"\' IBM.EssHA applicationLevelActivate"
    if(executeRASRepairCmd(t, f, cmd) != 0):
        msg = 'Execute applicationLevelActivate for HA adapter ' + HA_adapter + ' failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)

    msg = 'Sleep for one minute...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)
    
    #Check HA status after test starts
    msg = 'Check status of HA adapters after test completes'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if (public_interface.CheckHAStatus(f, t) == 1):
        msg = 'Not all HA adapter is available, please check the status of HA adapter'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Status of all HA adapters is good'
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
