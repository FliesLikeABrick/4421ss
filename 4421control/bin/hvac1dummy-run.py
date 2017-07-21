#!/usr/bin/env python3
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
print("Channel 1: now set back high, fans should be on")
		
