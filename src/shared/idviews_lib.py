"""
idviews library functions
"""

import os
import sys
import time
import pytest
from ipa_pytests.qe_class import multihost


def idview_add(host, viewname, desc=None, set_attr=None, addattr=None,
               alloption=None, raw=None, allraw=None):
    """Adding views """
    cmd_list = ['ipa', 'idview-add', viewname]
    if desc:
        cmd_list.append('--desc=' + desc)
    if set_attr:
        cmd_list.append('--setattr=' + set_attr)
    if addattr:
        cmd_list.append('--addattr=' + addattr)
    if alloption:
        cmd_list.append('--all')
    if raw:
        cmd_list.append('--raw')
    if allraw:
        cmd_list.append('--all', '--raw')
    check = host.run_command(cmd_list, raiseonerr=False)
    if check.returncode != 0:
        print ("Error in adding idview" + viewname)
    else:
        print (viewname + " added sucessfully")


def idview_del(host, viewname):
    """Deleting views """
    cmd_list = ['ipa', 'idview-del', viewname]
    if viewname:
        cmd_list.append(viewname)
    check = host.run_command(cmd_list, raiseonerr=False)
    return check


def idoverrideuser_add(host, viewname, user=None, uid=None, gid=None,
                       desc=None, login=None, gecos=None, shell=None,
                       key=None, homedir=None):
    """Adding useridoverride """
    cmd_list = ['ipa', 'idoverrideuser-add', viewname]
    if user:
        cmd_list.append(user)
    if uid:
        cmd_list.append('--uid=' + uid)
    if gid:
        cmd_list.append('--gidnumber=' + gid)
    if login:
        cmd_list.append('--login=' + login)
    if gecos:
        cmd_list.append('--gecos=' + gecos)
    if desc:
        cmd_list.append('--desc=' + desc)
    if shell:
        cmd_list.append('--shell=' + shell)
    if key:
        cmd_list.append('--key=' + key)
    if homedir:
        cmd_list.append('--homedir=' + homedir)
    check = host.run_command(cmd_list, raiseonerr=False)
    return check


def idoverrideuser_mod(host, viewname, user=None, uid=None, gid=None,
                       desc=None, login=None, gecos=None, shell=None,
                       key=None, homedir=None):
    """Modifying user information in view"""
    cmd_list = ['ipa', 'idoverrideuser-mod', viewname]
    if user:
        cmd_list.append(user)
    if uid:
        cmd_list.append('--uid=' + uid)
    if gid:
        cmd_list.append('--gidnumber=' + gid)
    if login:
        cmd_list.append('--login=' + login)
    if gecos:
        cmd_list.append('--gecos=' + gecos)
    if desc:
        cmd_list.append('--desc=' + desc)
    if shell:
        cmd_list.append('--shell=' + shell)
    if key:
        cmd_list.append('--key=' + key)
    if homedir:
        cmd_list.append('--homedir=' + homedir)
    check = host.run_command(cmd_list, raiseonerr=False)
    return check


def idoverrideuser_del(host, viewname, user=None):
    """Deleting overridden user in view"""
    cmd_list = ['ipa', 'idoverrideuser-del', viewname, user]
    if viewname:
        cmd_list.append('viewname')
    if user:
        cmd_list.append('user')
    check = host.run_command(cmd_list, raiseonerr=False)
    return check


def idoverridegroup_add(host, viewname, groupname, gid=None, desc=None):
    """Adding groupoverride for a group"""
    cmd_list = ['ipa', 'idoverridegroup-add', viewname, groupname]
    if gid:
        cmd_list.append('--gid=' + gid)
    if desc:
        cmd_list.append('--desc=' + desc)
    check = host.run_command(cmd_list, raiseonerr=False)
    return check


def idoverridegroup_del(host, viewname, groupname):
    """Deleting overridden user in view"""
    cmd_list = ['ipa', 'idoverridegroup-del', viewname, groupname]
    if viewname:
        cmd_list.append('viewname')
    if group:
        cmd_list.append('group')
    check = host.run_command(cmd_list, raiseonerr=False)
    return check


def idoverridegroup_mod(host, viewname, groupname, newgrp=None,
                        gid=None, desc=None, rename=None):
    """Modifying group override"""
    cmd_list = ['ipa', 'idoverridegroup-mod', viewname, groupname]
    if newgrp:
        cmd_list.append('--group-name=' + newgrp)
    if gid:
        cmd_list.append('--gid=' + gid)
    if desc:
        cmd_list.append('--desc=' + desc)
    if rename:
        cmd_list.append('--rename=' + rename)
    check = host.run_command(cmd_list, raiseonerr=False)
    return check


def idoverrideuser_find(host, viewname, anchor, desc=None,
                        login=None, uid=None, gecos=None,
                        gidnumber=None, homedir=None, shell=None):
    """find useroverride"""
    cmd_list = ['ipa', 'idoverrideuser-find', viewname, anchor]
    if desc:
        cmd_list.append('--desc=' + desc)
    if login:
        cmd_list.append('--login=' + login)
    if uid:
        cmd_list.append('--uid=' + uid)
    if gecos:
        cmd_list.append('--gecos=' + gecos)
    if gidnumber:
        cmd_list.append('--gidnumber=' + gidnumber)
    if homedir:
        cmd_list.append('--homedir=' + homedir)
    check = host.run_command(cmd_list, raiseonerr=False)
    return check
