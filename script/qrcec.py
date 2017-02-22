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


if __name__ == '__main__':

    # Check if the input arguments are valid
    logDir = '/home/root/BAT/log' 
    argc = len(sys.argv)
    if ((argc != 5) and (argc != 7)):
        print 'usage sample: qrcec.py -t mbxx -n 0(or 1)'
        exit (1)
        
    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16' and sys.argv[2] != 'mb15' and sys.argv[2] != 'mb17') or
         (sys.argv[3] != '-n') or
         (sys.argv[4] != '0' and sys.argv[4] != '1')
         ):
        print 'usage sample: qrcec.py -t mbxx -n 0(or 1)'
        exit (1)

    if ((argc == 7) and (sys.argv[5] == '-d')):        logDir = sys.argv[6]

    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'

    if(sys.argv[4] == '0'):
       sharkPort = 12301
    else:
       sharkPort = 12311

    (f, logName) = public_interface.CreateLogFile(sys.argv[0], sys.argv[2])

    # Log into CEC
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


    # Check status before test starts -- check if DS8K is in dual cluster mode
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



    # Execute command: /CPSS/testdaemon -l cpserver -2
    if(sharkPort == 12301):
        nod = '1'
    else:
        nod = '0'

    quiesceMsg = 'Executing command: /CPSS/testdaemon -l cpserver' + nod +  ' -2' + '\n'
    checkMsg = 'Executing command: cat /dev/cpss0/status/cpserver' + nod + '\n'
    resumeMsg =  'Executing command: /CPSS/testdaemon -l cpserver' + nod +  ' -3' + '\n'

    quiesceCmd = 'date;/CPSS/testdaemon -l cpserver' + nod + ' -2' + '\n'
    checkCmd = 'date;cat /dev/cpss0/status/cpserver' + nod + '\n'
    resumeCmd = 'date;/CPSS/testdaemon -l cpserver' + nod + ' -3' + '\n'
    
    public_interface.logMsg(quiesceMsg, 'KEY_MSG',f)

    ostr = public_interface.ExecuteCmd(quiesceCmd, t, f)
    ostr_element = ostr.split('\n')

    quiesceFlag = 0

    for i in range(0, len(ostr_element)):
        if('response information: 0 0 0' in ostr_element[i]):
            quiesceFlag = 1
            break
        else:
            continue

    if(quiesceFlag == 0):
        msg = 'CEC ' + nod + 'quiesce failure!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Quiesce CEC' + nod + ' executed sucessfully!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
            

    #Sleep for 10 seconds
    msg = 'sleep for 10 seconds, please wait...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(10)
    

    #Check whether CEC is in service mode 
    public_interface.logMsg(checkMsg, 'KEY_MSG',f)

    ostr = public_interface.ExecuteCmd(checkCmd, t, f)
    ostr_element = ostr.split('\n')

    quiesceFlag = 0
    for i in range(0, len(ostr_element)):
        if('SERVICE_MODE' in ostr_element[i]):
            quiesceFlag = 1
            break
        else:
            continue
            
    if(quiesceFlag == 0):
        msg = 'CEC ' + nod + ' is not in service mode after quiesce!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'CEC' + nod + ' is in service mode after quiesce'
        public_interface.logMsg(msg, 'KEY_MSG', f)
         
        
    #Sleep for 5 mintues before resuming CEC
    msg = 'sleep for 5 minutes, please wait...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(300)


    #Execute command: /CPSS/testdaemon -l cpserver -3
    public_interface.logMsg(resumeMsg, 'KEY_MSG',f)

    ostr = public_interface.ExecuteCmd(resumeCmd, t, f)
    ostr_element = ostr.split('\n')
    resumeFlg    = 0
    for i in range(0, len(ostr_element)):
        if('response information: 0 0 0' in ostr_element[i]):
            resumeFlg = 1
            break
        else:
            continue

    if(resumeFlg == 0):
        msg = 'CEC' + nod + ' failed to resume! Need to check the reason!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'CEC' + nod + ' resumed sucessfully!'
        public_interface.logMsg(msg, 'KEY_MSG', f)


    #Sleep 30 minutes after CEC resumes completed
    msg = 'sleep for 30 minutes, please wait...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(1800)
    
    #Check status after test completes  -- check if DS8K is in dual cluster mode
    msg = 'Check DS8K machine status after test completed'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    clusterMode = public_interface.machineStatusCheck(t, f)
    if (clusterMode == 1):
        msg = sharkAddr + ' is not in dual cluster mode, please check machine status'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Machine status of ' + SharkAddr + ' is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)

    public_interface.ScriptPassHandler(f, logName, logDir) 
