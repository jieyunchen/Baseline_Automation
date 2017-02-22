#!/usr/bin/env python
# -*- coding: utf-8 -*-

'Quiesce Resume DA test case '

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
        print 'usage sample: qrDA.py -t mbxx -c iss*\n'
        exit (1)

    if ( (sys.argv[1] != '-t') or
         (sys.argv[2] != 'mb12' and sys.argv[2] != 'mb16' and sys.argv[2] != 'mb15' and sys.argv[2] != 'mb17') or
         (sys.argv[3] != '-c') or
         ('iss' not in sys.argv[4])
         ):
        print 'usage sample: qrDA.py -t mbxx -c iss*\n'
        exit (1)

    if ((argc == 7) and (sys.argv[5] == '-d')):
        logDir = sys.argv[6]

    # the default DA configuration  
    # CEC0_OWNED_DA =['iss0' + m + n for m in '0246' for n in '25']
    # CEC1_OWNED_DA =['iss0' + m + n for m in '1357' for n in '25']
    
    # the host name     
    SharkAddr  = sys.argv[2] + 'h.tuc.stglabs.ibm.com'

    # the shark port for telnet
    if (int(sys.argv[4][-1]) % 2 == 0):
       sharkPort = 12301
    else:
       sharkPort = 12311
       
    # test DA card
    DACard = sys.argv[4]
    
    #create the log file   
    (f, logName) = public_interface.CreateLogFile(sys.argv[0], sys.argv[2])
    

    # login in the default owned  CEC
    msg = 'Connecting to ' + SharkAddr + ',' + 'port ' + str(sharkPort) + ' by default'
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
    msg3 = 'this cluster is not the affinity node of the DA card \nwe need to tranfer to the other cluster \n'
    msg4 = 'this cluster is the affinity node of the  DA card, continue the test \n'
    
    command1 = 'lsdev -Cc adapter |grep "' + DACard + '"'
    command2 = 'cat /dev/cpss0/status/' + DACard
    
    #check whether we installed this da card
    public_interface.logMsg(msg1, 'KEY_MSG', f)
    
    #flag_da indicate we have this card in this box when the value is not 0
    flag_da = 0
    
    omsg = public_interface.ExecuteCmd(command1, t, f)
    omsg_element = omsg.split ('\n')
    
    for i in range(1, len(omsg_element)):
        if (DACard in omsg_element[i]):
            flag_da = 1
            break
    if (flag_da == 0):
        msg = 'DA adapter ' + DACard + ' is not existed in DS8K ' + SharkAddr
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
    else:
        msg = 'DA adapter ' + DACard + ' is existed in DS8K ' + SharkAddr + ', continue the Test'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        
    #check whether we are on the affinity node of the test DA card
    public_interface.logMsg(msg2, 'KEY_MSG', f)
    
    #flag_own indicate we have this card in this lpar when the value is not 0
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
        
    #quiesce  DA adapter
    cmd = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA applicationLevelDeactivateRepair"

    msg = 'we are going to quiesce the DA card using the following command: \n'+ cmd
    public_interface.logMsg(msg, 'KEY_MSG', f)
    
    exitcode = executeRASRepairCmd(t, f, cmd, 0)

    if(exitcode != 0):
        msg = 'quiesce DA Adapter ' + DACard + ' command failure'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)
        
    else:
        msg = 'quiesce DA Adapter' + DACard + ' command succeed,test continue'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        
    #check whether we quiesce the DA card successfully
    cmd = 'cat /dev/cpss0/status/' + DACard
    omsg = public_interface.ExecuteCmd(cmd,t,f)
    omsg_element = omsg.split('\n')
    
    quiesce_flag = 0
    
    for i in range(0,len(omsg_element)):
        if('SERVICE_MODE' in omsg_element[i]):
            quiesce_flag = 1
            break
        else:
            pass
            
    if (quiesce_flag == 0):
        msg =  'quiesce DA Adapter ' + DACard + ' failed !'
        public_interface.logMsg(msg, 'KEY_MSG', f)
        public_interface.ScriptFailHandler(f, logName, logDir)          
    else:
        msg = 'quiesce DA Adapter ' + DACard + ' succeed!'
        public_interface.logMsg(msg, 'KEY_MSG', f)
            

    #Execute RAS repair command to resume the DA adapter

    command1 = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA systemLevelActivateRepair"   
    command2 = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA systemLevelVerifyRepair" 
    command3 = "runact -s 'logicalName==" + '"' + DACard + '"' + "' IBM.EssDA applicationLevelActivateRepair" 
    command4 = "/usr/lib/methods/fcfgissr -l issr -a " + DACard
    
    commandlist = [command1,command2,command3,command4]
    
    msg = "ISS adapter resume process - RAS repair:" + '\n' + command1 +'\n' + command2 +'\n' + command3 +'\n' + command4 +'\n'
    public_interface.logMsg(msg, 'KEY_MSG', f)
    
    for cmd in commandlist:

        exitcode = executeRASRepairCmd(t, f, cmd, 0) 
        
        if (exitcode != 0):
            msg =  "We failed at the DA Unfence process when we excute the commod:" + cmd + "\n"
            msg = msg + "please check the exit code,one of them must have something wrong:\n"
            msg = msg + "Exit Code = " + testMachine.exitcode + "\n"
            msg = msg + "Test Failed !!!"
            
            public_interface.logMsg(msg, 'KEY_MSG', f)
            public_interface.ScriptFailHandler(f, logName, logDir)
        
        else:
            msg = 'Sleep for one minute...'
            public_interface.logMsg(msg, 'KEY_MSG', f)
            sleep(60)
        
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
        
    #Check DA status after test complete
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
