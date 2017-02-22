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

def BATScriptTerminateHandler(f_log, f_prof, logName, logDir):
    f_log.close()
    f_prof.close()
    public_interface.TransformLogFile(logName, logDir)
    exit(0)

def CreateBATLogFile(testMachine, startTimeStr):
    logName = 'BATLOG_' + testMachine + '_' + startTimeStr
    f = file(logName, 'w')
    return (f, logName)

def CreateScriptLogDir(testMachine, startTimeStr):
    logDir = '/home/root/BAT/log/' + testMachine + '_' + startTimeStr
    isLogDirExist = os.path.exists(logDir)
    if (isLogDirExist == False):
        os.mkdir(logDir)
        return (0, logDir)
    else:
        return (1, logDir)
    
if __name__ == '__main__':
    
    # Check if the input arguments are valid
    argc = len(sys.argv)
    if ( argc != 3 or
         (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16' and sys.argv[2] != 'mb15' and sys.argv[2] != 'mb17')): 
        print 'usage sample: bat.py -t mbxx'
        exit (1)

    #Get BAT test stat time 
    pstr='%Y%m%d_%H%M_%S'
    startTime  = datetime.datetime.now()
    startTimeStr = startTime.strftime(pstr)

    # Make dir to save script log files 
    (retCode, logDir) = CreateScriptLogDir(sys.argv[2], startTimeStr)
    if (retCode == 1):
        print 'log Directory \"' + logDir + '\" already existed!!\n'
        exit(1)

    # Check if machine profile exists 
    profile_dir = '/home/root/BAT/profile/' + sys.argv[2] + '.profile'
    if (os.path.exists(profile_dir) == False):
        print profile_dir + ' does not exist...\n'
        exit(1)

    # Create BAT log file 
    (f_log, logName) = CreateBATLogFile(sys.argv[2], startTimeStr)

    # Display all the test variations to be executed
    i   = 1
    msg = 'Baseline Automation Tool Starting now...\n'
    f_prof = file(profile_dir)
    while True:
        line = f_prof.readline()
        if(len(line) == 0):
            break
        else:
            msg = msg + 'Test Variation-' + str(i) + '\t' + line
            i   = i  + 1
            
    public_interface.logMsg(msg, 'BAT_MSG', f_log)

            
    #Execute each test variation in the pre-defined test bucket
    passFlag = 0
    i        = 1 
    f_prof   = file(profile_dir)
    while True:
        line = f_prof.readline()
        if(len(line) == 0):
            break

        if (line[-1] == '\n'):
            line_len = len(line) - 1
            line = line[0:line_len]
        
        msg = 'Testing case-' + str(i) + ' \'' + line + '\''
        public_interface.logMsg(msg, 'BAT_MSG', f_log)

        # Get each test variation start time
        case_startTime = datetime.datetime.now()
        # Execute test variation
        msg = '/home/root/BAT/script/' + line + ' -d \'' + logDir + '\''
        retCode = os.system('/home/root/BAT/script/' + line + ' -d ' + '\'' + logDir + '\'')
        if (retCode != 0):
            msg = 'Test case-' + str(i) + ' \'' + line + '\' failed'
            public_interface.logMsg(msg, 'BAT_MSG', f_log)
            case_endTime  = datetime.datetime.now()
            public_interface.GetTestDurationTime(case_startTime, case_endTime, f_log, 'case', i)
            passFlag = 1 
            i = i + 1
            break
        else:
            msg = 'Test case-'  + str(i) + ' \'' + line + '\' passed'
            public_interface.logMsg(msg, 'BAT_MSG', f_log)
            case_endTime  = datetime.datetime.now()
            public_interface.GetTestDurationTime(case_startTime, case_endTime, f_log, 'case', i)
            i = i + 1

        #Sleep 5 minutes to invoke the next variation 
        msg = 'Sleep for 5 minutes...'
        public_interface.logMsg(msg, 'BAT_MSG', f_log)
        sleep(300)
    
    # Test bucket running summary 
    lastCaseNum = i - 1
    if (passFlag == 0):
        msg = str(lastCaseNum) + ' test variations all passed'
        public_interface.logMsg(msg, 'BAT_MSG', f_log)
    else:
        msg = 'Test case-' + str(lastCaseNum) + ' failed, ' + str(lastCaseNum - 1) + ' test variations passed'
        public_interface.logMsg(msg, 'BAT_MSG', f_log)

    # Get BAT test end time
    endTime = datetime.datetime.now()
    public_interface.GetTestDurationTime(startTime, endTime, f_log, 'bucket', 0)
    BATScriptTerminateHandler(f_log, f_prof, logName, '/home/root/BAT/log')

    
            
            
            
    
        

    
