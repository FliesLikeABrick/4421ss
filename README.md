# 4421ss
This is a collection of tools and scripts used at the AMC Center.  Please use/fork, and PRs are welcome!

![Inventory of Controls Targets](/doc/img/inventory.png?raw=true "")

The inventory of targets and accepted states are scraped from the list of scripts in the specified script directory.

Support is planned for additional scripts which can be hooked to detect the current state of a target.

![Status after Change](/doc/img/control.png?raw=true "")

Note: This is currently written with the expectation that it is run behind a reverse proxy or under a webserver which enforces authentication and/or is only used by known, trusted users.  Shell commands are executed with some minimal validation currently.

# To-Do
## 4421control
- Status script support
- Safer handling of shell commands
- "Are you sure" AJAX validation before executing commands
- Potential usage of authenticated (HTTP Basic) usernames to provide some role-based control
- Minimum on/off times, however this would require some state and database functionality
- Cache script inventory and/or test behavior with higher number of scripts and states.
