#!/usr/bin/env python3
import sys
sys.path.append('/kwh/lib')
import KWH_MySQL
import subprocess
# info on subprocess: https://docs.python.org/3/library/subprocess.html#converting-argument-sequence

#***************************************************
#   THIS FILE IS GOING TO REPLACE pulseStart.sh ****
#***************************************************

DB = KWH_MySQL.KWH_MySQL()
sql = "SELECT `key`, `value` FROM `config` WHERE `active`=1"

# constantly checking kwh environment variables from config table
# to turn on/turn off appropriate pulse channel
while True:
    records = DB.SELECT(sql)
    # dictionary of all key:value pair from config table
    config_var = {}
    for row in records:
        config_var[row[0]] = row[1]

    # take out the config variables for pulse channels
    config = [config_var['PU01'],
              config_var['PU02'],
              config_var['PU03'],
              config_var['PU04'],
              config_var['PU05'],
              config_var['PU06']]

    # execute/stop the corresponding python file for each pulse channel
    if config[0] == '1':
        pu01 = subprocess.Popen('/kwh/data_collectors/pulse/PU01.py')
    else
        pu01.terminate() 
        # pu01 HAS TO EXIST BEFOREHAND 
        # => INITIALLY, CONFIG VALUES FOR ALL PULSE CHANNELS HAS TO BE 1

    if config[1] == '1':
        pu02 = subprocess.Popen('/kwh/data_collectors/pulse/PU02.py')
    else
        pu02.terminate()

    if config[2] == '1':
        pu03 = subprocess.Popen('/kwh/data_collectors/pulse/PU03.py')
    else
        pu03.terminate()

    if config[3] == '1':
        pu04 = subprocess.Popen('/kwh/data_collectors/pulse/PU04.py')
    else
        pu04.terminate()

    if config[4] == '1':
        pu05 = subprocess.Popen('/kwh/data_collectors/pulse/PU05.py')
    else
        pu05.terminate()

    if config[5] == '1':
        pu06 = subprocess.Popen('/kwh/data_collectors/pulse/PU06.py')
    else
        pu06.terminate()

pi.stop()
