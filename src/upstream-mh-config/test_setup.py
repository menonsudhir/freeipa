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

           #/etc/hosts setup on sut
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

           #Setup resolv.conf on client machine
           if hosts[i]['role'] == "client":
             print(hosts[i]['role'])
             resolv = []
             for j in range(no_of_hosts):
               if hosts[j]['role'] != "client":
                 if j is 0:
                   resolv.append("echo nameserver "+hosts[j]['ip']+" > /etc/resolv.conf")
                 else:
                   resolv.append("echo nameserver "+hosts[j]['ip']+" >> /etc/resolv.conf")
             print(resolv)
             for k in range(no_of_hosts):
               if hosts[k]['role'] == "client":
                  for item in resolv:
                    subprocess.call(["ssh", "-o StrictHostKeyChecking=no", "root@"+hosts[k]['ip'], item])

    except yaml.YAMLError as exc:
        print(exc)

