#!/usr/bin/env python
import re
import subprocess

# Load environment variables
execfile("/KWH/datalogger/config/pyvars.py")
DEBUG = int(DEBUG)

# Setup local variables
delPath ="/KWH/datalogger/transceive/sms/smsDel.sh"
readPath = "/KWH/datalogger/transceive/sms/smsRead.sh"
sendPath = "/KWH/datalogger/transceive/sms/smsSend.sh"
readLog = "/KWH/datalogger/transceive/sms/read.log"
printOn = 0
useful = []


def singleConfigChange(option, commandFile):
    if DEBUG: print("Set "+option)
    if printOn: print("Group Check!!! ")
    if printOn: print(match.group(1))
    if printOn: print(match.group(2))

    #If password is good call the command file
    if printOn: print(ADMPW)
    if match.group(1) == ADMPW:
        if DEBUG: print("Password match")
        if DEBUG: print("Setting "+option+" to: "+match.group(2))
        p = subprocess.Popen([commandFile, str(match.group(2))])
        # wait until complete to start delete process
        p.communicate()
        if p.returncode == 0:
            if DEBUG: print(option+" set success")
            if DEBUG: print("Deleting sms #"+messNum[i])
            p = subprocess.Popen([delPath, messNum[i]])
            p.communicate()
            if p.returncode == 0:
                if DEBUG: print("Delete success")
            else:
                if DEBUG: print("Delete failed")
            if DEBUG: print("Executing: "+sendPath+" "+phoneNums[i]+" "+option+" set to: "+match.group(2))
            p = subprocess.Popen([sendPath, phoneNums[i], str(option+" set to: "+match.group(2))])
            p.communicate()
    else:
        if DEBUG: print("Wrong password")
        if DEBUG: print("Deleting sms #"+messNum[i])
        p = subprocess.Popen([delPath, messNum[i]])
        p.communicate()
        if p.returncode == 0:
            if DEBUG: print("Delete success")
        else:
            if DEBUG: print("Delete failed")
        #On password fail we intentionally do not respond
        #because it would help an attacker crack the password


# Read sms from sim memory into read.log
p = subprocess.Popen(readPath)
# Wait for smsRead to complete
p.communicate()
# Open read.log with fresh SMS memory contents
fileName = open(readLog, "r")

#Read in line by line
for line in fileName:
    lineIn = line.split()
    count  = 0 
    for element in lineIn:
        count = count + 1
    if count != 0:
        useful.append(lineIn)

if printOn: print ("The first pass: ")
if printOn: print useful
    
keep = []
parsing = []
for item in useful:
    if item[0] == "+CMGL:":
        parsing.append(item)
    else:
        keep.append(item)

if printOn: print("The 'Parsing' list holds: ")
if printOn: print(parsing)
if printOn: print(" ")
if printOn: print(" The 'Keep' list holds: ")
if printOn: print(keep)
if printOn: print(" ")
    
phoneNumbers = []
messageNumbers = []
messages = keep[0:len(keep)-1] #For some reason, the last element is showing as "ok"

if printOn: print(" The 'messages' list holds: ")
if printOn: print(messages)
if printOn: print(" ")
    
for item in parsing:
    messageNumbers.append(item[1])
    phoneNumbers.append(item[2])

# remove quotes and commas from phone numbers
for i, item in enumerate(phoneNumbers):
    phoneNumbers[i] = item.replace("\"", "")
    phoneNumbers[i] = item.replace(",", "")    

#Lists will keep the order, so
# if you need to access a certain element
# you can access by element number

messNum = []
for item in messageNumbers:
    for char in item:
        if char == "'":
            #do nothing
            #Skip this one
            if printOn: print(" Nothing ")
        if char == ',':
            break
        else:
            messNum.append(char)

if printOn: print("\n")
#FINAL LIST OF MESSAGE NUMBERS
if DEBUG: print("Message Numbers: ", messNum)

#Now finish parsing the phone numbers
phoneNums = []
for item in phoneNumbers:
#### Wonder if 8:20 is always good? ######################################
    phoneNums.append(item[8:20])

if printOn: print("\n")
#FINAL LIST OF PHONE NUMBERS        
if DEBUG: print("Phone Numbers: ", phoneNums)        

if printOn: print("\n")
#FINAL LIST OF MESSAGES
if DEBUG: print("Messages", messages)

if printOn: print("\n")                      

#if the message contents are not useful, then delete the message...
#TEST -- delete message number 2...

# Run through the elements in the messages list
#and determine whether the message is valid
#if it is, move to the next item
#if it is not, delete it from the list -- update messageNum
#to that value so it can be deleted

reset = re.compile(\
r"\w*\s*(\d{4})#RESET#\s*\w*")
#group 1 
stationId = re.compile(\
r"\w*\s*(\d{4})#BST:(\d{5})#\s*\w*")
#group 1 and 2
setInquiryPass = re.compile(\
r"\w*\s*(\d{4})#BPS:(\d{4}),(\d{4})#\s*\w*")
#group 1, 2 and 3
setServerDNS = re.compile(\
r"\w*\s*(\d{4})#GDN:([A-z\.]*)\!#\s*\w*")
#changed \d{13} to \w* and escaped the ! that followed
#group 1 and 2
setServerPort = re.compile(\
r"\w*\s*(\d{4})#GIP:(\d{1,5})#\s*\w*")
#group 1 and 2
setupAPN = re.compile(\
r"\w*\s*(\d{4})#GAN:(\w*)\!#\s*\w*")
#changed \d{6} to \w* and escaped the ! that followed
#group 1 and 2
inquiryGSM = re.compile(\
r"\w*\s*(\d{4})#E1#\s*\w*")
#group 1
setDigitalInputParams = re.compile(\
r"\w*\s*(\d{4})#(DIN[1-6]):([0-4]),([0-1]{4}),([0-3]{6})#\s*\w*")
#group 1, 2, 3, 4 and 5
setPulseCounter = re.compile(\
r"\w*\s*(\d{4})#(DIP[1-6]):(\d{8})#\s*\w*")
#group 1, 2 and 3
analogIn = re.compile(\
r"\w*\s*(\d{4})#(ADN[0-1])(\d:[0-2]),(\d.\d{3}),(\d.\d\{3}),(\d.\d{3}),(\d.\d{3}),(\d.\d{3}),([0,1]{4}),([0-3]{6})#\s*\w*")
#groups 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
tempAnalogIn = re.compile(\
r"\w*\s*(\d{4})#(ADN1[1,2]):([0-2]),(\d.\d{3}),(\d.\d{3}),([0-1]{4}),([0-3]{6})#\s*\w*")
#groups 1, 2, 3, 4, 5, 6, 7
inquiryE2 = re.compile(\
r"\w*\s*(\d{4})#E2#\s*\w*")
#group 1
inquiryEE = re.compile(\
r"\w*\s*(\d{4})#EE#\s*\w*")
#group 1

commandList = [reset, stationId, setInquiryPass, setServerDNS, setServerPort, setupAPN, inquiryGSM,\
 setDigitalInputParams, setPulseCounter, analogIn, tempAnalogIn, inquiryE2, inquiryEE] 

#File paths for processing
resetPath = "/KWH/datalogger/transceive/sms/commands/reset.sh"
inqGSMPath = "/KWH/datalogger/transceive/sms/commands/inquiryGSM.sh"
setDigInPath = "/KWH/datalogger/transceive/sms/commands/setDigitalIn.sh"
setPulsePath = "/KWH/datalogger/transceive/sms/commands/setPulsePath.sh"

portPath = "/KWH/datalogger/transceive/sms/commands/port.sh"
staPath = "/KWH/datalogger/transceive/sms/commands/sta.sh"
setInqPassPath = "/KWH/datalogger/transceive/sms/commands/inq.sh"
domainPath = "/KWH/datalogger/transceive/sms/commands/domain.sh"
setApnPath = "/KWH/datalogger/transceive/sms/commands/apn.sh"

#Outside Basic KP Functionality 
analogInPath = "/KWH/datalogger/transceive/sms/commands/analogIn.sh"
tempAnalogInPath = "/KWH/datalogger/transceive/sms/commands/tempAnalogIn.sh"
inqE2Path = "/KWH/datalogger/transceive/sms/commands/inqE2.sh"
inqEEPath = "/KWH/datalogger/transceive/sms/commands/inqEE.sh" 


i = 0
for index, item in enumerate(messages):
    fullMessage = ' '.join(item)
    if printOn: print(fullMessage)
    for command in commandList:
        if printOn: print(i)
        #if printOn: print(command.search(fullMessage))
        match = command.search(fullMessage) 
        if match:
            #Keep it and break to check the next
            if printOn: print("Got a match!")
            #Process then delete

            #Execute the appropriate processing file
            if command == reset:
                if DEBUG: print("reset")
            elif command == stationId:
		singleConfigChange("Station ID", staPath)
	    elif command == setInquiryPass:
		singleConfigChange("Inquiry Password", inqPath)
            elif command == setServerDNS:
		singleConfigChange("Server Domain", domainPath)
            elif command == setServerPort:
		singleConfigChange("Server Port", portPath)                
            elif command == setupAPN:
		singleConfigChange("APN", apnPath)
            elif command == inquiryGSM:
                if DEBUG: print("inquiry GSM")
            elif command == setDigitalInputParams:
                if DEBUG: print("set digital input params")
            elif command == setPulseCounter:
                if DEBUG: print("set pulse counter")
            elif command == analogIn:
                if DEBUG: print("analog in")
            elif command == tempAnalogIn:
                if DEBUG: print("temperature analog in")
            elif command == inquiryE2:
                if DEBUG: print("inquiry E2")
            elif command == inquiryEE:
                if DEBUG: print("inquiry EE")
            #First delete the item from the file (subprocess)
            ###subprocess.Popen([delPath,str(messNum[i])])                   

            #Then delete the message contents, message number and phone number from the lists
            # messages, messNum, phoneNums
            ###del messages[i]
            ###del messNum[i]
            ###del phoneNums[i]
            #if printOn: print(" Updated lists: ")
            if printOn: print("messages: ")
            if printOn: print(messages)
            if printOn: print("message numbers: ")
            if printOn: print(messNum)
            if printOn: print("phone numbers: ")

      	    #messages has more items that messNum, having to increment i
	    #in here to no what messNum we are on - hopefully there's a better
	    #way
	    i = i + 1

        else:
            #Delete it
            #if DEBUG == 0: #save odd messages in debug mode
	    #	subprocess.Popen([delPath, messNum[i]])
	    if printOn: print("")

