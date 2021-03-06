# 4421ss
This is a collection of tools and scripts used at the AMC Center.  Please use/fork, and PRs are welcome!

## 4421control
A lightweight means to expose scripts for controls on Raspberry Pi and other platforms.  The original use case was using a RPi with relay board to control some mechanical equipment at the AMC center 
![Inventory of Controls Targets](/doc/img/inventory.png?raw=true "")

The inventory of targets and accepted states are scraped from the list of scripts in the specified script directory.

Support is planned for additional scripts which can be hooked to detect the current state of a target.

![Status after Change](/doc/img/control.png?raw=true "")

Note: This is currently written with the expectation that it is run behind a reverse proxy or under a webserver which enforces authentication and/or is only used by known, trusted users.  Shell commands are executed with some minimal validation currently.

## Requirements
- Python3
- pyYAML
### 4421control To-Do
- Status script support
- Safer handling of shell commands
- "Are you sure" AJAX validation before executing commands
- Potential usage of authenticated (HTTP Basic) usernames to provide some role-based control
- Minimum on/off times, however this would require some state and database functionality
- Cache script inventory and/or test behavior with higher number of scripts and states.
- Some day - allow one front instance of 4421control to be configured with a list of downstream control APIs (other instances of 4421control) to expose via the one unified GUI
