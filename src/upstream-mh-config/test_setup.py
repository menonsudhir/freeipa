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
        no_of_hosts = len(hosts)
        for i in range(no_of_hosts):
           etchostname = "echo "+hosts[i]['name']+" > /etc/hostname"
           subprocess.call(["ssh", "-o StrictHostKeyChecking=no", "root@"+hosts[i]['ip'], etchostname])
           print(etchostname)
           cmd = []
           for j in range(no_of_hosts):
             if j is 0:
               cmd.append("echo "+hosts[j]['ip']+" "+hosts[j]['name']+" > /etc/hosts")
             else:
               cmd.append("echo "+hosts[j]['ip']+" "+hosts[j]['name']+" >> /etc/hosts")
           print(cmd)
           for k in range(no_of_hosts):
             print(cmd[k])
             subprocess.call(["ssh", "-o StrictHostKeyChecking=no", "root@"+hosts[i]['ip'], cmd[k]])
    except yaml.YAMLError as exc:
        print(exc)

