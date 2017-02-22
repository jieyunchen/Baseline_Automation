#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telnetlib
import string
import sys
import datetime
import os
import commands

from time import sleep
from sys import stderr

sys.path.append('/home/root/BAT/lib') 
import public_interface

def moveEssniLog(logDir):
    mv_cmd = 'mv ~/BAT/log/ni*.log ' + logDir
    os.system(mv_cmd)
    
if __name__ == '__main__':
    
    # Check if the input arguments are valid
    logDir = '/home/root/BAT/log'
    argc = len(sys.argv)
    if ((argc != 3) and (argc != 5)):
        print '******usage sample : dscliEssni.py -t mbxx******'
        exit (1)    

    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16' and sys.argv[2] != 'mb15' and sys.argv[2] != 'mb17')
         ):
        print '******usage sample : dscliEssni.py -t mbxx******'
        exit(1)

    if ((argc == 5) and (sys.argv[3] == '-d')):
        logDir = sys.argv[4]

    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'
    sharkPort = 12301

    (f, logName) = public_interface.CreateLogFile(sys.argv[0], sys.argv[2])    

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

    # Execute the DSCLI-ESSNI test
    msg = 'Executing command: /usr/java6/bin/java -classpath ...'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    
    (status, msg) = commands.getstatusoutput('/usr/java6/bin/java -classpath /opt/ibm/dscli/lib//ESSNIClient.jar:/opt/ibm/dscli/lib//dsclihelp.jar:/opt/ibm/dscli/lib//dscli.jar:/opt/ibm/dscli/lib//logger.jar:/opt/ibm/dscli/lib//ibmjsse.jar:/opt/ibm/dscli/lib//dscliauto.jar DscliAutomRun -hmc ' + sys.argv[2] + 'h -user admin -passwd tucs0n -outputdir ' + logDir + ' -dsclipath /opt/ibm/dscli/dscli -runtype standard -sfi 1')
    public_interface.logMsg(msg, 'KEY_MSG', f)

    if (status == 0 and '<RETURN_CODE>SUCCESS</RETURN_CODE>' in msg):
        msg = 'DSCLI scripts test completed successfully!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
    else:
        msg = 'DSCLI test failed! Unexpected return code.'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        moveEssniLog(logDir)
        public_interface.ScriptFailHandler(f, logName, logDir)

    # Check status after test ends
    msg = 'Check DS8K machine status after test completed'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    clusterMode = public_interface.machineStatusCheck(t, f)
    if (clusterMode == 1):
        msg = sharkAddr + ' is not in dual cluster mode, please check machine status'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        moveEssniLog(logDir)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Machine status of ' + SharkAddr + ' is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)

    moveEssniLog(logDir)
    public_interface.ScriptPassHandler(f, logName, logDir)
    
