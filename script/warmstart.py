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
        print 'usage sample: warmstart.py -t mbxx -n 0(or 1)'
        exit (1)
        
    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16' and sys.argv[2] != 'mb15' and sys.argv[2] != 'mb17') or
         (sys.argv[3] != '-n') or
         (sys.argv[4] != '0' and sys.argv[4] != '1')
         ):
        print 'usage sample: warmstart.py -t mbxx -n 0(or 1)'
        exit (1)

    if ((argc == 7) and (sys.argv[5] == '-d')):
        logDir = sys.argv[6]
        
    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'

    if (sys.argv[4] == '0'):
       sharkPort = 12301
    else:
       sharkPort = 12311
        
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

    #Execute command "getdebug warmstart" on DS8K
    msg = 'Executing command: getdebug warmstart'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'date; getdebug warmstart' + '\n'
    public_interface.ExecuteCmd(cmd, t, f)

    #Sleep for one minute
    msg = 'sleep for 1 minute, please wait...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(60)

    # Check status after test completes  -- check if DS8K is in dual cluster mode
    msg = 'Check DS8K machine status after test completed'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    clusterMode = public_interface.machineStatusCheck(t, f)
    if (clusterMode == 1):
        msg = SharkAddr + ' is not in dual cluster mode, please check machine status'
        public_interface.logMsg(msg, 'KEY_MSG', f)
    	public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Machine status of ' + SharkAddr + ' is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)
    
    public_interface.ScriptPassHandler(f, logName, logDir)
