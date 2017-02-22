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
        print 'usage sample: haFastload.py -t mbxx'
        exit (1)
    
    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16' and sys.argv[2] != 'mb15' and sys.argv[2] != 'mb17')
         ):
        print 'usage sample: haFastload.py -t mbxx'
        exit (1)

    if ((argc == 5) and (sys.argv[3] == '-d')):
        logDir = sys.argv[4]

    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'
    fastload   = 'cpssflupdate -l '
    adapter    = []

    (f,logName) = public_interface.CreateLogFile(sys.argv[0], sys.argv[2])

    # log into CEC
    msg = 'Connecting to ' + SharkAddr + ',' + 'port ' + str(12301)
    public_interface.logMsg(msg, 'KEY_MSG', f)
    (returnCode, t) = public_interface.TelentToCEC(SharkAddr, 12301, f)
    if (returnCode == 1):
        msg = 'Failed to telnet to ' + SharkAddr
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Telnet to ' + SharkAddr + ' successfully!'
        public_interface.logMsg(msg, 'KEY_MSG', f) 

   # Check status before test starts -- check DS8K is in dual cluster mode
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

    # Execute the HA fastload test for each HA card
    msg = 'Executing command: lsdev -Cc adapter | grep \'cpssfc[0-9]\\{3\\} \''
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'date; lsdev -Cc adapter | grep \'cpssfc[0-9]\\{3\\} \'' + '\n'
    ostr = public_interface.ExecuteCmd(cmd, t, f)
    
    ostr_element = ostr.split('\n')
    for i in range(0, len(ostr_element)):
        if (ostr_element[i].startswith('cpssfc')):
            adapter.append(ostr_element[i][0:len('cpssfc003')])

    for i in range(0, len(adapter)):
        msg = 'Check HA adapter status before running HA fastload'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        if (public_interface.CheckHAStatus(f, t) == 1):
            msg = 'Not all HA adapter is available, please check the status of HA adapter before running HA fastload'
            public_interface.logMsg(msg, 'KEY_MSG', f)
            public_interface.ScriptFailHandler(f, logName, logDir)
        msg = 'Executing comand: cpssflupdate -l ' + adapter[i]
        public_interface.logMsg(msg, 'KEY_MSG', f)
        cmd = 'date; cpssflupdate -l ' + adapter[i] + ';' + "echo \"exitcode:$?\"" + '\n'
        ostr = public_interface.ExecuteCmd(cmd, t, f)

        returnCode = 1
        exitCode = 1
        ostr_element = ostr.split('\n')
        for j in range(1, len(ostr_element) - 1):
            if ('command OS_BEGIN_FASTLOAD rc = 0' in ostr_element[j]):
                returnCode = 0
            if ('exitcode:0' in ostr_element[j]):
                exitCode = 0
                
        if ((returnCode == 0) and (exitCode == 0)):
            msg = 'HA fastload running on adapter ' + adapter[i] + ' completed successfully!'
            public_interface.logMsg(msg, 'KEY_MSG', f)
        else:
            msg = 'HA fastload running on adapter ' + adapter[i] + ' failed! Unexpected return code or exit code'
            public_interface.logMsg(msg, 'KEY_MSG', f)
            public_interface.ScriptFailHandler(f, logName, logDir)

        sleep(60)

    # Check status after test ends
    msg = 'Check HA adapters after test completed'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if (public_interface.CheckHAStatus(f, t) == 1):
        msg = 'Not all HA adapter is available, please check the status of HA adapter before running HA fastload'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Status of all HA adapters is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)

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
