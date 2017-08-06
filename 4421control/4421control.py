#! /usr/bin/env python3
"""
API and UI application for 4421control.

Notes:
_CFG is used globally to store the default and user configurations, as well as
"Derived" configurations (sanitized paths+inputs, compiled expressions, etc)

"""
from flask import Flask,render_template
import subprocess
import sys,os
import glob
import traceback
import syslog
import yaml
import re
from argparse import ArgumentParser
from pprint import PrettyPrinter

pp = PrettyPrinter()
app = Flask(__name__)
@app.route("/")
def menu():
    pp.pprint(_TARGETS)
    updateStatus()
    pp.pprint(_TARGETS)
    return render_template("index.html",targets=_TARGETS,cfg=_CFG)

# Update target to desired state
# Returns 404 if the target does not exist
# Returns 400 if the desired state does not exist
# Returns default 404 if no state or target is specified in URL
@app.route("/control/<target>/<state>")
def control(target,state):
    command = {'name':"Control %s, to state %s" % (target,state) }
    command['script'] = _TARGETS[target]['states'][state]['script']
    if not target in _TARGETS:
        # target does not exist
        command['output'] = 'Exception encountered during script execution: target %s does not exist\n%s' % (target)
        # (don't syslog invalid requests)
        return render_template("control.html",commands = [ command ],cfg=_CFG), 404
    if not state in _TARGETS[target]['states']:
        # target does not exist
        command['output'] = 'Exception encountered during script execution: target %s does not offer state %s' % (target,state) 
        # (don't syslog invalid requests)
        return render_template("control.html",commands = [ command ],cfg=_CFG), 400

    try:
        command['output'] = subprocess.check_output(_CFG['scripts']['directory']+command['script'],shell=True).decode("utf-8")
    except Exception as e:
        command['output'] = 'Exception encountered during script execution: ' + str(e)
    # Fire off syslog for this state change
    log(command.__str__())
    return render_template("control.html",commands = [ command ],cfg=_CFG)


# Index the scripts in the script directory, according to the glob and pattern
# also load the script's additional info from yaml, and status script location (if any)
# 'status' scripts are just stored as a special state for now.
def getTargets():
    scripts = [scriptname.split(os.sep)[-1] for scriptname in glob.glob(_CFG['scripts']['directory']+_CFG['scripts']['glob']) ]
    targets = {}
    for script in scripts:
        matches = _CFG['scripts']['regex'].match(script)
        state = {}
        state['name'] = matches.group('state') # yaml can override (not implemented)
        state['info'] = '' # from yaml (not implemented)
        state['type'] = matches.group('type')
        state['script'] = matches.group(0)
        if matches.group('target') not in targets:
            targets[matches.group('target')]={'states':{}}
        targets[matches.group('target')]['states'][matches.group('state')] = state
    # sort the scripts and states by name now to avoid doing it repeatedly later
    return targets
def updateStatus():
    # update status of all entries in _TARGETS that have a status script
    for target,targetinfo in _TARGETS.items():
        pp.pprint(targetinfo)
        if 'status' in targetinfo['states']:
            _TARGETS[target]['status'] = subprocess.check_output(_CFG['scripts']['directory']+targetinfo['states']['status']['script'],shell=True).decode("utf-8").strip()
def log(entry):
    """ Handle logging to syslog and files """
    if _CFG['syslog']['enable']:
        syslog.syslog(entry)
def loadConfig(ucf,dcf):
    # open defaults configuration file
    try:
        with open(dcf) as yf:
            cfg = yaml.load(yf.read())
    except Exception as e:
        sys.stderr.write("Failed to load configuration defaults from file %s\n%s\n" % (dcf,str(e)))
        sys.exit(1)

    # If no user config file is specified, return the defaults.
    if ucf is None:
        return cfg
    # open user configuration file
    try:
        with open(ucf) as yf:
            userCfg = yaml.load(yf.read())
    except FileNotFoundError as e:
        sys.stderr.write("Failed to open configuration file %s\n%s\n" % (ucf,str(e)))
        sys.stderr.write("Copy 4421control.cfg.example.yaml to 4421control.cfg.yaml or\n")
        sys.stderr.write("use --defaults to run without a configuration file, which will all default values (not recommended).\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write("Failed to load configuration file %s\n%s\n" % (ucf,str(e)))
        sys.exit(1)

    # update the default's config sections
    # Alternatively this could recursively update the dcfg dict with cfg
    # in the meantime, however, this requires a line for each section of the config
    # and potentially more depth/care if layers of the config should not be wholesale replaced
    for section in userCfg.keys():
        if section in cfg:
            cfg[section].update(userCfg[section])
        else:
            cfg[section] = userCfg[section]
    return cfg
def initialize():

    ##### Scripts Config #####
    # directory containing state and status scripts
    # os.path.join is used to add the trailing OS path separator if it is not already present in the config
    _CFG['scripts']['directory'] = os.path.join(os.path.expanduser(_CFG['scripts']['directory']), '')
    if not os.path.isdir(_CFG['scripts']['directory']):
        sys.stderr.write("Scripts directory %s does not exist or is not a directory\n" % _CFG['scripts']['directory'])
        sys.exit(2)
    try:
        _CFG['scripts']['regex'] = re.compile(_CFG['scripts']['pattern'])
    except Exception as e:
        sys.stderr.write("Could not compile script pattern %s\n%s\n" % (_CFG['scripts']['pattern'],str(e)))
        sys.exit(2)

    ##### Logging Config #####
    # set up syslog, if enabled
    if _CFG['syslog']['enable']:
        if _CFG['syslog']['ident']:
            syslog.openlog(ident=_CFG['syslog']['ident'])


if __name__ == "__main__":
    # ideally take this filename as a default, and override with a command line option
    parser = ArgumentParser(description='UI and API server for 4421control: https://github.com/FliesLikeABrick/4421ss/')
    parser.add_argument('--defaults', action='store_true',help='Ignore configuration file.  Default: False')
    parser.add_argument('--config', default=os.path.dirname(os.path.realpath(__file__)) + os.sep + "4421control.cfg.yaml",help="Configuration file location.  Default: 4421control.cfg.yaml")
    parser.add_argument('--defaultconfig', default=os.path.dirname(os.path.realpath(__file__)) + os.sep + "4421control.cfg.defaults.yaml",help="Configuration defaults file location.  Default: 4421control.cfg.defaults.yaml.  Normal users should never change this.")
    args = parser.parse_args()

    if args.defaults:
        sys.stderr.write("--defaults specified, running with default configuration.\n")
        cfgFile = None

    _CFG = loadConfig(args.config,args.defaultconfig)
    initialize()
    _TARGETS = getTargets()
    # exit status codes:
    # 1 - config issue
    # 2 - initialization issue
    app.run(host='::',debug=True)

