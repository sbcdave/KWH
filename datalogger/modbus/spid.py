#!/usr/bin/env python
import wiringpi
import spidev
import time 

#config spi
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 2400
spi.mode = 0b01

#config R/W toggle pin
io = wiringpi.GPIO(wiringpi.GPIO.WPI_MODE_PINS)
TxEnable = 2
io.pinMode(TxEnable,io.OUTPUT)

#send
io.digitalWrite(TxEnable,io.HIGH)

sendData = [0,64,16,4,1,64,69,16,4,1,0,72,20,116,123\
,0,64,16,4,1]

#spi.writebytes(sendData)

#receive
#io.digitalWrite(TxEnable,io.LOW)

#recvData = spi.readbytes(36)
recvData = spi.xfer(sendData)

print recvData