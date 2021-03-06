#!/usr/bin/env python
import socket
import time
import signal
import serial
import subprocess

# Load environment variables
execfile("/KWH/datalogger/config/pyvars.py")
DEBUG = int(DEBUG)

# Global variables
RESET_LIMIT = 3

def signal_handler(signal, frame):
    if DEBUG > 0: log('SIGINT received...Closing SIM Server\n')
    sim.close()
    s.close()
    cs.close()
    exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Log function
def log(logText):
    with open("/KWH/datalogger/transceive/simServer.log", "a") as log:
	log.write(logText)

# Reset the SIM card
def reset():
    execfile("/KWH/datalogger/transceive/reset_sim.py")
    if DEBUG > 0: log("Sleeping 5 for SIM reboot and reconfigure!\n")
    time.sleep(4)

# Logs in simServer.log if the env variable DEBUG is 1
if DEBUG > 0: log("Starting SIM Server\n")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 9999
port_chosen = False

if DEBUG > 0: log("Starting port selection\n") 

# Find an open port for the service
while not port_chosen:
    try:
	s.bind((host, port))
        port_chosen = True
    except:
	if DEBUG > 0: log("Port "+str(port)+" in use\n")
	port = port + 1

# Update the env variables with the chosen active SIM_PORT
with open("/KWH/datalogger/config/SIM_PORT", "w") as SIM_PORT:
    SIM_PORT.write(str(port))

if DEBUG > 0: log("SIM_PORT: "+str(port)+"\n")

reset()
# Configure block
execfile("/KWH/datalogger/config/pyvars.py")
DEBUG = int(DEBUG)
if DEBUG > 1: log("Configuration variables reloaded\n")    
subprocess.Popen("/KWH/datalogger/transceive/ttyAMA0_setup.sh")
if DEBUG > 1: log("Executed ttyAMA0_setup.sh\n")    
time.sleep(1)

if DEBUG > 0: log("Listening...\n")


s.listen(1)
sim = serial.Serial('/dev/ttyAMA0', 115200, timeout=5)
sim.flushInput()
sim.flushOutput()

# Daemon listen on SIM_PORT for SIM commands
while True:
    # Waits for a command
    cs,addr = s.accept()

    # Configure block
    execfile("/KWH/datalogger/config/pyvars.py")
    DEBUG = int(DEBUG)
    if DEBUG > 1: log("Configuration variables reloaded\n")    
    subprocess.Popen("/KWH/datalogger/transceive/ttyAMA0_setup.sh")
    if DEBUG > 1: log("Executed ttyAMA0_setup.sh\n")    

    # Beginning to process received command
    cmd = cs.recv(1024)
    if DEBUG > 1: log("Received: "+cmd+"\n")

    # Send command to SIM
    try:
	sim.write(cmd)

        if DEBUG > 0: log("Wrote to sim: "+cmd+"\n")

	# Command specific delays
        if cmd == "AT+CGATT=1\n" \
            or cmd == "AT+CIFSR\n" \
            or cmd[0] == "\#":
            time.sleep(3)
        elif cmd == "AT+CIPSTART=\"TCP\",\""+DOMAIN+"\",\""+PORT+"\"\n" \
            or cmd == "AT+CIICR\n" \
            or cmd == "AT+CIPSTART=\"TCP\",\"time.nist.gov\",\"37\"\n":
            time.sleep(4)
        else:
            time.sleep(.3)

        # Get SIM response
        fromSIM = sim.inWaiting()

        # If no response, restart SIM, reset config, and retry
        count = 0
        while fromSIM < 1 and count < RESET_LIMIT:
	    # Check one more time before resetting
            time.sleep(1)
            fromSIM = sim.inWaiting()
            if fromSIM > 0:
                break
            if DEBUG > 0: log(str(fromSIM)+" bytes from SIM. Resetting SIM!\n")
            # No luck! Reset
            reset()
	    execfile("/KWH/datalogger/config/pyvars.py")
	    DEBUG = int(DEBUG)
	    if DEBUG > 1: log("Configuration variables reloaded\n")    
	    subprocess.Popen("/KWH/datalogger/transceive/ttyAMA0_setup.sh")
	    if DEBUG > 1: log("Executed ttyAMA0_setup.sh\n")    
	    time.sleep(1)

            count += 1
	    # Resend command and check again for response
            try:
                sim.write(cmd)
	    except:
	        log("EXCEPTION: Write Failed")
            if DEBUG > 0: log("Wrote to sim: "+cmd+"\n")
            time.sleep(0.5)
            fromSIM = sim.inWaiting()

        # Get SIM response
        if DEBUG > 0: log("Bytes to read: "+str(fromSIM)+"\n")
        resp = sim.read(fromSIM)
        if DEBUG > 0: log("Sim response: "+resp+"\n")
	# Tell the client if there was "No response" failure
        if resp == "":
            resp = "No response"
        cs.send(resp)
        if DEBUG > 1: log("Response sent to: "+str(addr)+"\n")

        # Check for any other response data in SIM memory
        fromSIM = sim.inWaiting()
        if fromSIM > 0:
            if DEBUG > 0: log("Bytes to read: "+str(fromSIM)+"\n")
            resp = sim.read(fromSIM)
            if DEBUG > 0: log("Sim response: "+resp+"\n")
            cs.send(resp)
            if DEBUG > 1: log("Response sent to: "+str(addr)+"\n")

        sim.flushInput()
        sim.flushOutput()
    
        time.sleep(.5)
        cs.close()
    except:
        log("EXCEPTION: Write Failed")
        reset()
	execfile("/KWH/datalogger/config/pyvars.py")
        DEBUG = int(DEBUG)
	if DEBUG > 1: log("Configuration variables reloaded\n")    
        subprocess.Popen("/KWH/datalogger/transceive/ttyAMA0_setup.sh")
        if DEBUG > 1: log("Executed ttyAMA0_setup.sh\n")    
        time.sleep(1)

    cs.close()
    if DEBUG > 1: log("Client connection closed\n")
