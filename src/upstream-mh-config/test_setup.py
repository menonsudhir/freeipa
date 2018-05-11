"""
-Setting hostname and /etc/hosts of test vms
"""

from __future__ import print_function
import yaml
import sys
import subprocess

with open((sys.argv[1:])[0]) as stream:
    try:
        code = yaml.load(stream)
        hosts = code['domains'][0]['hosts']
        for host in hosts:
           #print(host['ip'],host['name'])
           etchostname = "echo "+host['name']+" > /etc/hostname"
           print(etchostname)
           etchost = "echo "+host['ip']+" "+host['name']+" > /etc/hosts"
           print(etchost)
           subprocess.call(["ssh", "root@"+host['ip'], etchostname])
           subprocess.call(["ssh", "root@"+host['ip'], etchost])
    except yaml.YAMLError as exc:
        print(exc)
