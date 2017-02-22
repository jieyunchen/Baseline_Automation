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
    if ((argc != 3) and (argc != 5)):
        print 'usage sample: shuffle_global_data.py -t mbxx'
        exit (1)

    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16')
         ):
        print 'usage sample: shuffle_global_data.py -t mbxx'
        exit (1)

    if ((argc == 5) and (sys.argv[3] == '-d')):
        logDir = sys.argv[4]
        
    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'
    adapter    = []
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

    #Execute command "dacmd -x setwhite -a gd=0x400" on DS8K
    msg = 'Executing command: dacmd -x setwhite -a gd=0x400'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'date; dacmd -x setwhite -a gd=0x400' + '\n'
    public_interface.ExecuteCmd(cmd, t, f)

    msg = 'Sleep for 90 secs, please wait...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    
    sleep(90)

    #Execute command "dacmd -x setwhite -a gd=0x0" on DS8K
    msg = 'Executing command: dacmd -x setwhite -a gd=0x0'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'date; dacmd -x setwhite -a gd=0x0' + '\n'
    public_interface.ExecuteCmd(cmd, t, f)

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
    
