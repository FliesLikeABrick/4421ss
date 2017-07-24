#! /usr/bin/env python3
from flask import Flask,render_template
import subprocess
import sys,os
import glob
import traceback
import syslog

# directory containing operation scripts
# of name format target-state.py
SCRIPTDIR = "bin"+os.sep
syslog.openlog(ident='4421control/app.py')

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
        command['output'] = subprocess.check_output(SCRIPTDIR+command['script'],shell=True).decode("utf-8")
    except Exception as e:
        command['output'] = 'Exception encountered during script execution: ' + str(e)
    # Fire off syslog for this state change
    syslog.syslog(command.__str__())
    return render_template("control.html",commands = [ command ])

# Ideally this would be cached, but currently doesn't hurt performance (at least with low number of scripts)
def getScripts():
    scripts = [scriptname.split(os.sep)[-1] for scriptname in glob.glob(SCRIPTDIR+'*-*.py') ]
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
if __name__ == "__main__":
    app.run(host='::',debug=True)

