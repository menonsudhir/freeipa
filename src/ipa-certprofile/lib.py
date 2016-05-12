import re
import os
import pytest


def certprofile_run(options=None):
    """
    Helper function to perform IPA certprofile operation

    @params: op = operation need to be perform. Default is 'show'
    @params: opts = dictionary containing following
                    host = host machine command needs to be run
                    key-value pair of commandline options
    """
    if not options:
        print("ERROR: Certprofile_run : Options not specified")
        return

    host = options['host']
    op = options.get('op', 'show')
    exp_code = int(options.get('exp_code', '0'))
    exp_output = options.get('exp_output', None)
    cmd = ['ipa', 'certprofile-' + op]
    for key in options.keys():
        if key == 'host' or key == 'exp_code' or\
           key == 'exp_output' or key == 'op':
            continue
        if options[key] == '':
            cmd.append(key)
        else:
            if op == 'del':
                continue
            if op == 'show' and key != 'out':
                continue
            cmd.append('--' + key + '=' + options[key])

    print("Execute : %s " % (" ".join(cmd)))
    cmd = host.run_command(cmd, raiseonerr=False)
    if cmd.returncode != exp_code:
        print("Expected returncode : %s" % (exp_code))
        print("Returned returncode : %s" % (cmd.returncode))
        pytest.xfail("Failed to run ipa certprofile-%s with "
                     "given parameter" % (op))

    if exp_output is not None:
        print("Expected output : %s" % (exp_output))
        if cmd.stdout_text and exp_output not in cmd.stdout_text:
            print("Returned stdout : %s" % (cmd.stdout_text))
            pytest.xfail("Return code matched but failed to verify "
                         "command output")
        if cmd.stderr_text and exp_output not in cmd.stderr_text:
            print("Returned stderr : %s" % (cmd.stderr_text))
            pytest.xfail("Return code matched but failed to verify "
                         "command output")


def create_cert_cfg(opts=None):
    """
    Helper function to create Certificate configuration

    @params: mh = multihost
    @params: opts = dictionary containing following
                    host = host machine command needs to be run
                    name = name of certificate cfg
                    desc = description of certificate cfg
                    opfile = output configuration file path
    """
    if not opts:
        return
    host = opts['host']
    if not host:
        return
    cfg = host.get_file_contents(opts['cacert'])
    cfg = re.sub(r'profileId=.*\n?', 'profileId=' + opts['name'] + "\n", cfg)
    cfg = re.sub(r'^desc=.*\n?', 'desc=' + opts['desc'] + "\n", cfg)
    cfg = re.sub(r'^name=.*\n?', 'name=' + opts['name'] + "\n", cfg)

    cfgput = opts.get('opfile', '/tmp/' + opts['name'] + '.cfg')
    cfgput = cfgput.replace(' ', '_')
    host.put_file_contents(cfgput, cfg)


def caacl_run(options=None):
    """
    Helper function to perform IPA caacl operation

    @params: opts = dictionary containing following
                    host = host machine command needs to be run
                    key-value pair of commandline options
    """
    host = options['host']
    op = options['op']

    exp_code = int(options.get('exp_code', '0'))
    exp_output = options.get('exp_output', None)
    hosts = options.get('hosts', None)
    hostgroups = options.get('hostgroups', None)
    profiles = options.get('certprofiles', None)
    services = options.get('services', None)
    users = options.get('users', None)
    groups = options.get('groups', None)

    cmd = ['ipa', 'caacl-' + op]
    for key in options.keys():
        if key == 'host' or key == 'exp_code' or\
           key == 'exp_output' or key == 'op':
            continue
        if options[key] == '':
            cmd.append(key)
        else:
            if op == 'del' or op == 'disable' or op == 'enable':
                continue
            elif op == 'show' and key != 'out':
                continue
            elif (op == 'add-host' or op == 'remove-host') and hosts is not None:
                if isinstance(hosts, str):
                    cmd.append('--hosts=' + hosts)
                elif isinstance(hosts, list):
                    for host in hosts:
                        cmd.append('--hosts=' + host)
            elif (op == 'add-host' or op == 'remove-host') and hostgroups is not None:
                if isinstance(hostgroups, str):
                    cmd.append('--hostgroup=' + hostgroups)
                elif isinstance(hostgroups, list):
                    for hostgroup in hostgroups:
                        cmd.append('--hostgroup=' + hostgroup)
            elif (op == 'add-profile' or op == 'remove-profile') and profiles is not None:
                if isinstance(profiles, str):
                    cmd.append('--certprofiles=' + profiles)
                elif isinstance(profiles, list):
                    for profile in profiles:
                        cmd.append('--certprofiles=' + profile)
            elif (op == 'add-service' or op == 'remove-service') and services is not None:
                if isinstance(services, str):
                    cmd.append('--services=' + services)
                elif isinstance(services, list):
                    for service in services:
                        cmd.append('--services=' + service)
            elif (op == 'add-user' or op == 'remove-user') and users is not None:
                if isinstance(users, str):
                    cmd.append('--users=' + users)
                elif isinstance(users, list):
                    for user in users:
                        cmd.append('--users=' + user)
            elif (op == 'add-user' or op == 'remove-user') and groups is not None:
                if isinstance(groups, str):
                    cmd.append('--groups=' + groups)
                elif isinstance(groups, list):
                    for group in groups:
                        cmd.append('--groups=' + group)
            else:
                if options[key] == 'noarg':
                    cmd.append('--' + key)
                else:
                    cmd.append('--' + key + '=' + options[key])

    print("Execute : %s " % (" ".join(cmd)))
    cmd = host.run_command(cmd, raiseonerr=False)
    if cmd.returncode != exp_code:
        print("Expected returncode : %s" % (exp_code))
        print("Returned returncode : %s" % (cmd.returncode))
        pytest.xfail("Failed to run ipa caacls-%s with "
                     "given parameter" % (op))

    if exp_output is not None:
        print("Expected output : %s" % (exp_output))
        if cmd.stdout_text and exp_output not in cmd.stdout_text:
            print("Returned stdout : %s" % (cmd.stdout_text))
            pytest.xfail("Return code matched but failed to verify "
                         "command output")
        if cmd.stderr_text and exp_output not in cmd.stderr_text:
            print("Returned stderr : %s" % (cmd.stderr_text))
            pytest.xfail("Return code matched but failed to verify "
                         "command output")
