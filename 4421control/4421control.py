#! /usr/bin/env python3
from flask import Flask,render_template
import subprocess
import sys,os
import glob
import traceback
import syslog
import yaml

app = Flask(__name__)

@app.route("/")
def menu():

    return render_template("index.html",targets=getScripts())

# Update target to desired state
# Returns 404 if the target does not exist
# Returns 400 if the desired state does not exist
# Returns default 404 if no state or target is specified in URL
@app.route("/control/<target>/<state>")
def control(target,state):
    scripts = getScripts()
    command = {'name':"Control %s, to state %s" % (target,state) }
    command['script'] = "%s-%s.py" % (target,state)
    if not target in scripts:
        # target does not exist
        command['output'] = 'Exception encountered during script execution: target %s does not exist' % target
        # (don't syslog invalid requests)
        return render_template("control.html",commands = [ command ]), 404
    if not state in scripts[target]['states']:
        # target does not exist
        command['output'] = 'Exception encountered during script execution: target %s does not offer state %s' % (target,state) 
        # (don't syslog invalid requests)
        return render_template("control.html",commands = [ command ]), 400

    try:
        command['output'] = subprocess.check_output(_CFG['scripts']['directory']+command['script'],shell=True).decode("utf-8")
    except Exception as e:
        command['output'] = 'Exception encountered during script execution: ' + str(e)
    # Fire off syslog for this state change
    log(command.__str__())
    return render_template("control.html",commands = [ command ])

# Ideally this would be cached, but currently doesn't hurt performance (at least with low number of scripts)
def getScripts():
    scripts = [scriptname.split(os.sep)[-1] for scriptname in glob.glob(_CFG['scripts']['directory']+'*-*.py') ]
    scriptDirectory = {}
    for script in scripts:
        try:
            target, state = script.split('.')[0].split('-')
            if target in scriptDirectory:
                scriptDirectory[target]['states'].append(state)
            else:
                # Status is N/A because another set of scripts needs to be added for querying states of targets
                # but this starts laying some groundwork
                scriptDirectory[target] = {'states':[state],'status':'N/A'}
        except Exception as e:
            sys.stderr.write("Failed to parse script %s"% script)
            traceback.print_exc(file=sys.stderr)
            continue
    return scriptDirectory
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
        sys.stderr.write("Failed to open configuration file %s\n%s\n" % (dcf,str(e)))
        sys.exit(1)
    # open user configuration file
    try:
        with open(ucf) as yf:
            userCfg = yaml.load(yf.read())
    except Exception as e:
        sys.stderr.write("Failed to open configuration file %s\n%s\n" % (ucf,str(e)))
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
    # directory containing state and status scripts
    # os.path.join is used to add the trailing OS path separator if it is not already present in the config
    _CFG['scripts']['directory'] = os.path.join(os.path.expanduser(_CFG['scripts']['directory']), '')
    if not os.path.isdir(_CFG['scripts']['directory']):
        sys.stderr.write("Scripts directory %s does not exist or is not a directory\n" % _CFG['scripts']['directory'])
        sys.exit(1)

    # set up syslog, if enabled
    if _CFG['syslog']['enable']:
        if 'ident' in _CFG['syslog']:
            syslog.openlog(ident=_CFG['syslog']['ident'])

if __name__ == "__main__":
    # ideally take this filename as a default, and override with a command line option
    cfgFile=os.path.dirname(os.path.realpath(__file__)) + os.sep + "4421control.cfg.yaml"
    defaultCfgFile=os.path.dirname(os.path.realpath(__file__)) + os.sep + "4421control.cfg.defaults.yaml"
    _CFG = loadConfig(cfgFile,defaultCfgFile)
    initialize()
    app.run(host='::',debug=True)

