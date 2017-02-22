#!/usr/bin/env python
# -*- coding: utf-8 -*-

' Fence/Unfence DA  test case '

__author__ = 'Zhou Hong'

import telnetlib
import string
import sys
import datetime
import os

from time import sleep
from sys import stderr

#import VEP common interface here
sys.path.append('/home/root/BAT/lib')
import public_interface

def executeRASRepairCmd(t, f, cmd, flag):
    msg = 'Executing command: ' + cmd
    public_interface.logMsg(msg, 'KEY_MSG', f)
    cmd = 'date;' + cmd + ';' + "echo \"exitcode:$?\"" + '\n'
    omsg = public_interface.ExecuteCmd(cmd, t, f)
    omsg_element = omsg.split('\n')
    exitCode     = 1
    retCode      = 1
    for i in range(0, len(omsg_element)):
        if ('exitcode:0' in omsg_element[i]):
            exitCode = 0
        if ('returnCode = 0' in omsg_element[i]):
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
        print 'usage sample: fenceDA.py -t mbxx -c iss*\n'
        exit (1)
        
    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16' and sys.argv[2] != 'mb15' and sys.argv[2] != 'mb17') or
         (sys.argv[3] != '-c') or
         ('iss' not in sys.argv[4])
         ):
        print '\n usage sample: fenceDA.py -t mbxx -c iss*\n'
        exit (1)

    if ((argc == 7) and (sys.argv[5] == '-d')):
        logDir = sys.argv[6]

    # the default DA configuration  
    # CEC0_OWNED_DA =['iss0' + m + n for m in '0246' for n in '25']
    # CEC1_OWNED_DA =['iss0' + m + n for m in '1357' for n in '25']
    
    # the host name     
    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'

    # the shark port for telnet
    if ( int(sys.argv[4][-1]) % 2 == 0):
       sharkPort = 12301
    else:
       sharkPort = 12311
       
    # test DA card
    DACard = sys.argv[4]
    
    #create the log file   
    (f, logName) = public_interface.CreateLogFile(sys.argv[0], sys.argv[2])
    

    # login in the default owned  CEC
    msg = 'Connecting to ' + SharkAddr + ',' + 'port ' + str(sharkPort) + 'by default'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    (returnCode, t) = public_interface.TelentToCEC(SharkAddr, sharkPort, f)
    if (returnCode == 1):
        msg = 'Failed to telnet to ' + SharkAddr
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Telnet to ' + SharkAddr + ' successfully!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        

    # check which CEC owned the DACard 
    msg1 = 'check whether we install this da card in the box\n'
    msg2 = 'check whether we are on the affinity node of the test DA card\n'
    msg3 = 'this cluster is not the affinity node of the DA card and we need to tranfer to the other cluster \n'
    msg4 = 'this cluster is the affinity of the DA card, continue the test \n'
    
    command1 = 'lsdev -Cc adapter |grep "' + DACard + '"'
    command2 = 'cat /dev/cpss0/status/' + DACard
    
    #check whether we installed this da card
    public_interface.logMsg(msg1, 'KEY_MSG', f)
    
    #flag_da indicates we have this card in this box when the value is not 0
    flag_da = 0
    
    omsg = public_interface.ExecuteCmd(command1, t, f)
    omsg_element = omsg.split ('\n')
    
    for i in range(1, len(omsg_element)):
        if (DACard in omsg_element[i]):
            flag_da = 1
            break
        else:
            continue
            
    if (flag_da == 0):
        msg = 'DA adapter ' + DACard + 'does not exist in DS8K ' + SharkAddr
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'DA adapter ' + DACard + ' does exist in DS8K ' + SharkAddr + ',continue the Test'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        
    #check whether we are on the affinity node of this test DA card
    public_interface.logMsg(msg2, 'KEY_MSG', f)
    
    affinity_index = 0
    
    omsg = public_interface.ExecuteCmd(command2, t, f)
    omsg_element = omsg.split ('\n')
    
    
    for i in range(0, len(omsg_element)):
        if ('DA_AFFINITY_TO_NODE' in omsg_element[i]):
            affinity_index = i
            break
        else:
            continue
     
    if (affinity_index == 0):
        msg = 'we can not determin the affinity node of this DA card, exit the test,please check this machine'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
        
    if ('DA_AFFINITY_TO_NODE0' in omsg_element[affinity_index]):
        if(sharkPort != 12301):
            public_interface.logMsg(msg3, 'KEY_MSG', f)
            sharkPort = 12301
            t.close()
            (returnCode, t) = public_interface.TelentToCEC(SharkAddr, sharkPort, f)
            if (returnCode == 1):
                msg = 'Failed to telnet to ' + SharkAddr
                public_interface.logMsg(msg, 'KEY_MSG', f)
                public_interface.ScriptFailHandler(f, logName, logDir)
            else:
                msg = 'Telnet to ' + SharkAddr + ' successfully!'
                public_interface.logMsg(msg, 'KEY_MSG', f)          
        else:
            public_interface.logMsg(msg4, 'KEY_MSG', f)
            
    else:
        if(sharkPort != 12311):
            public_interface.logMsg(msg3, 'KEY_MSG', f)
            sharkPort = 12311
            t.close()
            (returnCode, t) = public_interface.TelentToCEC(SharkAddr, sharkPort, f)
            if (returnCode == 1):
                msg = 'Failed to telnet to ' + SharkAddr
                public_interface.logMsg(msg, 'KEY_MSG', f)
                public_interface.ScriptFailHandler(f, logName, logDir)
            else:
                msg = 'Telnet to ' + SharkAddr + ' successfully!'
                public_interface.logMsg(msg, 'KEY_MSG', f)          
        else:
            public_interface.logMsg(msg4, 'KEY_MSG', f)  

            
   # Check Machine status before test starts 
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
        msg = 'Status of all DA adapters is good, Continue the test!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        

    #Fence DA adapter    
    cmd_get_hexcode = "dacmd -x adapt | grep " + DACard + " | awk '{print $3}'"

    msg = 'we are going to get the hexcode of the da card using the command:\n' + cmd_get_hexcode 
    public_interface.logMsg(msg, 'KEY_MSG', f)
    
    #get the hexcode for the test da card
    omsg = public_interface.ExecuteCmd(cmd_get_hexcode, t, f)
    omsg_element = omsg.split('\n')
    hexcode_index = -1
    for i in range(0, len(omsg_element)):
        if('0x' in omsg_element[i]):
            hexcode_index = i
            break
        else:
            continue
    
    if(hexcode_index == -1):
        msg = 'failed to get the hex code for the test da card:' + DACard
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:    
        DA_hexcode = omsg_element[hexcode_index]
    
    cmd_fence = "dacmd -x adaptreset -a node=" + DA_hexcode
    cmd_exitcode = "echo \"exitcode:$?\""
    
    msg = 'we are going to fence the DA card using the following command for three times \n' + cmd_fence
    public_interface.logMsg(msg, 'KEY_MSG', f)
    
    for i in range(3):
        
        if i == 0:
            public_interface.logMsg('the first time', 'KEY_MSG', f)
        elif i == 1:
            public_interface.logMsg('the second time', 'KEY_MSG', f)
        else:
            public_interface.logMsg('the third time', 'KEY_MSG', f)
            
        public_interface.ExecuteCmd(cmd_fence, t, f)
        omsg = public_interface.ExecuteCmd(cmd_exitcode,t,f)
        omsg_element = omsg.split('\n')
        
        exitcode_flag = False
        for i in range(0, len(omsg_element)):
            if 'exitcode:0' in omsg_element[i]:
                exitcode_flag = True
                break
            else:
                continue
                
        if(exitcode_flag == False):
            msg = "test case failed at the cmd: " + cmd_fence
            public_interface.logMsg(msg, 'KEY_MSG', f)
            public_interface.ScriptFailHandler(f, logName, logDir)
            
        else:
            msg = "test case will sleep for 1 min here..."
            public_interface.logMsg(msg, 'KEY_MSG', f)
            sleep(60)
            
    #Check the status of DA adapter
    msg = 'Check if the DA adapter ' +  DACard + ' is fenced or not'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if(public_interface.CheckIfCardFenced(t, f, DACard) != 0):
        msg = 'DA adapter ' + DACard + ' has not been fenced after 1 min. sleep'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'DA adapter ' + DACard + ' has been fenced, test continue '
        public_interface.logMsg(msg, 'KEY_MSG', f)

    #Sleep 3 minutes before executing RAS repair
    msg = "Sleep 3 minutes before executing RAS repair..."
    public_interface.logMsg(msg, 'KEY_MSG', f)
    sleep(180)
        
    #Execute RAS repair command to repair DA adapter

    command1 = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA applicationLevelDeactivateRepair"
    command2 = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA systemLevelActivateRepair"   
    command3 = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA systemLevelVerifyRepair" 
    command4 = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA applicationLevelActivateRepair" 
    command5 = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA resetDATakeover"  
    
    commandlist = [command1,command2,command3,command4,command5]
    
    msg = "ISS adapter repair process - RAS repair:" + '\n' + command1 +'\n' + command2 +'\n' + command3 +'\n' + command4 +'\n' + command5 +'\n'    
    public_interface.logMsg(msg, 'KEY_MSG', f)
    
    for cmd in commandlist:

        if (cmd != command5):
            exitcode = executeRASRepairCmd(t, f, cmd, 0)
            if (exitcode == 1):
                msg =  "We failed at the DA Unfence process when we excute the commod:" + cmd + "\n"
                msg = msg + "please check the exit code,it must have something wrong:\n"
                msg = msg + "Exit Code = " + str(exitcode) + "\n"
                msg = msg + "Test Failed !!!"
                public_interface.logMsg(msg, 'KEY_MSG', f)
                public_interface.ScriptFailHandler(f, logName, logDir)
            else:
                msg = 'Sleep for one minute...'
                public_interface.logMsg(msg, 'KEY_MSG', f)
                sleep(60)
            
        else:
            exitcode = executeRASRepairCmd(t, f, cmd, 1) 
            if (exitcode == False):
                msg =  "We failed at the DA Unfence process when we excute the commod:\n" + cmd + "\n"
                msg = msg + "please check the exit code or the return code,one of them must have something wrong:\n"
                public_interface.logMsg(msg, 'KEY_MSG', f)
                public_interface.ScriptFailHandler(f, logName, logDir)
        

    
    # Make enclosure related to ISS adapter available
    # cmd = "/etc/methods/fcfgissr -l issr -a " + DACard
    # public_interface.ExecuteCmd(cmd, t, f)
    
    # omsg = public_interface.ExecuteCmd(cmd_exitcode,t,f)
    # omsg_element = omsg.split('\n')
        
    # if 'exitcode:0' not in omsg_element[2]:
        # msg = "test case failed at the cmd: " + cmd
        # public_interface.logMsg(msg, 'KEY_MSG', f)
        # public_interface.ScriptFailHandler(f, logName, logDir)  
    
    #check SE status after the test complete
    msg = 'Check status of SE status after test RAS repair action'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    if (public_interface.CheckEnclosureStatus(f, t) == 1):
        msg = 'Not all SE is available, please check the status of SE'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'Status of all SE is good'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        
    #Check DA status after test completes
    msg = 'Check status of DA adapters after test RAS repair action'
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
