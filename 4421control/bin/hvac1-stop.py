#! /usr/bin/env python3
##################################################

#           P26 ----> Relay_Ch1
#			P20 ----> Relay_Ch2
#			P21 ----> Relay_Ch3

##################################################
#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

print("Setup The Relay Module is [success]")

# Ensure channel 1 is high (not calling for start)
GPIO.output(Relay_Ch1,GPIO.HIGH)

GPIO.output(Relay_Ch2,GPIO.LOW)
print("Channel 1: Set LOW for 1s")
time.sleep(1)
GPIO.output(Relay_Ch2,GPIO.HIGH)
print("Channel 1: now set back high, fans should be off")
		
