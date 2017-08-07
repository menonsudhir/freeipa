"""
Shared support for ipa host control
"""

import paths


def host_mod(host, hostname, options=None, raiseonerr=True):
    """
    Helper function to modify service
    :param host: multihost
    :param hostname: hostname
    :param options: options without --
    """
    if not options:
        options = {}
    cmd = [paths.IPA, 'host-mod']
    for key, value in options.iteritems():
        key = "--" + key
        if value == '':
            cmd.append(key)
        elif isinstance(value, (tuple, list)):
            for item in value:
                cmd.extend((key, item))
        else:
            cmd.extend((key, value))
    cmd.append(hostname)
    print("Executing : [{0}]".format(" ".join(cmd)))
    return host.run_command(cmd, raiseonerr=raiseonerr)


def host_add(host, hostname, options={}, raiseonerr=False):
    """
    Helper function to add host
    :param host: multihost
    :param hostname: hostname
    :param options: options without --
    """
    cmd = host_find(host, hostname=hostname)
    if "Host name: {0}".format(hostname) in cmd.stdout_text:
        return type('RetObj', (object,),
                    dict(returncode=0,
                         stdout_text='Host already exists',
                         stderr_text=''))

    cmd = [paths.IPA, 'host-add']
    cmd.append(hostname)
    for key, value in options.iteritems():
        key = "--" + key
        if value == '':
            cmd.append(key)
        elif isinstance(value, (tuple, list)):
            for item in value:
                cmd.extend((key, item))
        else:
            cmd.extend((key, value))
    print("Executing: [{0}]".format(" ".join(cmd)))
    return host.run_command(cmd, raiseonerr=raiseonerr)


def hostgroup_member_add(host, hg=None, options={}, raiseonerr=False):
    """
    Helper function to add host to hostgroup
    :param host: multihost
    :param hg: Hostgroup name
    :param options: options without --
    """
    cmd = [paths.IPA, 'hostgroup-add-member']
    for key, value in options.iteritems():
        key = "--" + key
        if value == '':
            cmd.append(key)
        elif isinstance(value, (tuple, list)):
            for item in value:
                cmd.extend((key, item))
        else:
            cmd.extend((key, value))
    cmd.append(hg)
    print("Executing: [{0}]".format(" ".join(cmd)))
    return host.run_command(cmd, raiseonerr=raiseonerr)


def hostgroup_find(host, hg=None, raiseonerr=False):
    """
    Helper function to find host in hostgroup
    :param host: multihost
    :param hg: hostgroup name
    """
    cmd = [paths.IPA, 'hostgroup-find', hg]
    print("Executing: [{0}]".format(" ".join(cmd)))
    return host.run_command(cmd, raiseonerr=raiseonerr)


def host_find(host, hostname, raiseonerr=False):
    """
    Helper function to find host
    :param host: Multihost
    :param hostname: Hostname to find
    :param raiseonerr: Boolean
    """
    cmd = [paths.IPA, 'host-find', "--hostname={0}".format(hostname)]
    print("Executing [{0}]".format(" ".join(cmd)))
    return host.run_command(cmd, raiseonerr=raiseonerr)


def host_del(host, hostname, raiseonerr=False):
    """
    Helper function to delete host
    :param host: multihost
    :param hostname: hostname to delete
    """
    cmd = host_find(host, hostname=hostname)
    if "Host name: {0}".format(hostname) not in cmd.stdout_text:
        return type('RetObj', (object,),
                    dict(returncode=1,
                         stdout_text='Host does not exists',
                         stderr_text=''))
    cmd = [paths.IPA, 'host-del', hostname]
    print("Executing [{0}]".format(" ".join(cmd)))
    return host.run_command(cmd, raiseonerr=raiseonerr)

