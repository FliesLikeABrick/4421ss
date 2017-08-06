#!/usr/bin/env python3
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

# Ensure channel 2 is HIGH (not break)

#Control the Channel 1
print("Channel 1: Set LOW for 1s")
time.sleep(1)
with open("/tmp/status",'w') as f:
    print("run",file=f)
print("Channel 1: now set back high, fans should be on")
		
