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
