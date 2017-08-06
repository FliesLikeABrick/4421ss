#! /usr/bin/env python3
# demo dummy control script for 4421control
# just sleeps and writes to /tmp/status
##################################################

#           P26 ----> Relay_Ch1
#			P20 ----> Relay_Ch2
#			P21 ----> Relay_Ch3

##################################################
#!/usr/bin/python
# -*- coding:utf-8 -*-
import time

print("Setup The Relay Module is [success]")

# Ensure channel 1 is high (not calling for start)
print("Channel 1: Set LOW for 1s")
with open("/tmp/status",'w') as f:
    print("stop",file=f)
time.sleep(1)
print("Channel 1: now set back high, fans should be off")
		
